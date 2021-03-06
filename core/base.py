__author__ = 'Quentin Kaiser'
__email__ = 'quentin@gremwell.com'
execfile('VERSION')
import __builtin__
import sys
import json
import traceback
import imp
import os
import signal
import re
import time
import random
import string
from zipfile import ZipFile
import subprocess

import framework
from androguard.core import androconf
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis.analysis import *
from androguard.core.analysis.ganalysis import *
from android import *
from jinja2 import Environment, FileSystemLoader
import codecs

try:
    import scapy.all as scapy
except ImportError:
    import scapy
try:
    import scapy_http.http
except ImportError:
    from scapy.layers import http
from scapy.error import Scapy_Exception

# define colors for output
# note: color in prompt effects
# rendering of command history
__builtin__.N = '\033[m'  # native
__builtin__.R = '\033[31m'  # red
__builtin__.G = '\033[32m'  # green
__builtin__.O = '\033[33m'  # orange
__builtin__.B = '\033[34m'  # blue]]]]]'

__builtin__.loaded_modules = {}


class severity:
    LOW, MEDIUM, HIGH = range(3)


class category:
    INFORMATION_DISCLOSURE, SQLINJECTION = range(2)


class APKScanner(framework.module):
    """Main module that will instrument all submodules fromm modules directory.

    Help the application to perform:
        - APK extraction
        - Static analysis
        - Dynamic analysis
        - Reporting
    """

    def __init__(self, options):
        framework.module.__init__(self, None)
        self.apk_filename = options.apk
        self.apk = None
        self.avd = None
        self.analysis = {
            "start_time": 0,
            "end_time": 0,
            "application": {
                "package": None,
                "name": None,
                "path": None,
                "size": 0
            },
            "modules": {},
            "vulnerabilities": []
        }
        self.loaded_category = {}
        self.loaded_modules = __builtin__.loaded_modules
        self.load_apk()
        self.load_modules()
        self.static_only = options.static_only
        self.verbose = options.verbose
        self.headless = options.headless

    def on_boot(self, avd):
        self.alert("AVD is up")
        self.deploy()

    def deploy(self):
        self.output("Installing APK...")
        self.avd.install(self.apk.filename)
        self.avd.remount()
        self.avd.push(
            "%s/libs/busybox-android/busybox-android" % self.root_dir,
            "/system/xbin/busybox"
        )
        self.avd.shell("chmod 777 /system/bin/android-remote-install.sh")
        self.avd.unlock()

        self.output("Launching application ...")
        for a in self.get_activities():
            if a["exported"] and len(a["intent_filters"]) and \
                            a["intent_filters"][0]["action"] == "android.intent.action.MAIN" \
                    and a["intent_filters"][0]["category"] == "android.intent.category.LAUNCHER":
                cmd = "am start -n %s/%s" % (self.apk.get_package(), a["name"])
                output = self.avd.shell(cmd)

    def analyze(self, module=None):
        """
        :return:
        """
        self.analysis["start_time"] = int(time.time())
        self.analysis["application"]["package"] = self.apk.package
        self.analysis["application"]["path"] = self.apk.filename
        self.analysis["application"]["name"] = self.apk.filename
        self.analysis["application"]["size"] = os.path.getsize(self.apk.filename)

        self.fry()
        if not self.static_only:
            self.output("Searching AVD ...")
            self.avd = self.find_avd()
            if not self.avd.isrunning:
                self.output("Launching new emulator [%s]" % self.avd.name)
                self.avd.launch(self.on_boot, headless=self.headless)
            else:
                self.output("AVD found [emulator-%d running %s]" % (self.avd._id, self.avd.name))
                self.deploy()

            if not os.path.exists("analysis/%s/" % self.apk.get_package()):
                os.mkdir("%s/analysis/%s/" % (self.root_dir, self.apk.get_package()))

            self.output("Setting up logcat logger...")
            if not os.path.exists("%s/analysis/%s/logs" %
                    (self.root_dir, self.apk.get_package())):
                os.mkdir("%s/analysis/%s/logs" % (self.root_dir, self.apk.get_package()))
            self.subprocesses.append(
                self.avd.logcat(
                    "%s/analysis/%s/logs/logcat_pkg.log" % (
                        self.root_dir,
                        self.apk.get_package()
                    ),
                    tag=self.apk.get_package()
                )
            )
            self.subprocesses.append(
                self.avd.logcat(
                    "%s/analysis/%s/logs/logcat_full.log" % (
                        self.root_dir,
                        self.apk.get_package()
                    ),
                    tag=None
                )
            )

            self.output("Launching network capture ...")
            if not os.path.exists("%s/analysis/%s/network" %
                    (self.root_dir, self.apk.get_package())):
                os.mkdir("%s/analysis/%s/network" %
                         (self.root_dir, self.apk.get_package()))
            self.avd.start_traffic_capture(
                "%s/analysis/%s/network/capture.pcap" %
                (self.root_dir, self.apk.get_package())
            )

        try:
            modules = self.loaded_modules
            if module is not None:
                if module in self.loaded_modules:
                    modules = [x for x in self.loaded_modules if x == module]
                else:
                    self.error("This module do not exists.")

            for k in modules:
                m = sys.modules[self.loaded_modules[k]].Module(self.apk, self.avd)
                self.output("Running %s ..." % (m.info['Name']))
                r = {
                    "start_time": int(time.time()),
                    "name": m.info["Name"],
                    "run": m.module_run(verbose=self.verbose),
                    "end_time": int(time.time())
                }
		del m
                for v in r["run"]["vulnerabilities"]:
                    self.alert(v["name"])
                self.analysis["modules"][k] = r

        except Exception as e:
            self.error(str(e))

        if self.avd is not None:
            self.alert("Execute manual testing then hit <Enter>. We'll see if you can beat me at finding vulns ...")
            raw_input("")
            self.output("Teleporting data ...")
            self.teleport(self.avd)

            for pid in self.subprocesses:
                os.kill(pid + 1, signal.SIGTERM)

            self.output("Stopping network capture ...")
            self.avd.stop_traffic_capture()
            self.output("Uninstalling APK ...")
            self.avd.uninstall(self.apk.get_package())
            self.output("Shutting down AVD...")
            self.avd.shutdown()

        self.analysis["end_time"] = int(time.time())

    def summary(self):
        from datetime import date
        summary = "\n\n Analysis done - %s - %s\n" % (self.apk.get_package(), date.today().strftime("%Y%m%d"))
        summary += "\n\t* Disassembled code: %s/analysis/%s/code" % (self.root_dir, self.apk.get_package())
        summary += "\n\t* Logcat files: %s/analysis/%s/logs" % (self.root_dir, self.apk.get_package())
        summary += "\n\t* Network capture: %s/analysis/%s/network" % (self.root_dir, self.apk.get_package())
        summary += "\n\t* Device storage dump: %s/analysis/%s/storage" % (self.root_dir, self.apk.get_package())
        summary += "\n\t* HTML report: %s/analysis/%s/report.html" % (self.root_dir, self.apk.get_package())
        summary += "\n\n"
        print summary

    def load_apk(self):
        """
            Load the APK with Androguard.
        """
        try:
            if not os.path.exists(self.apk_filename):
                self.error("The APK file do not exists")
            else:
                if androconf.is_android(self.apk_filename) == "APK":
                    a = apk.APK(self.apk_filename, zipmodule=2)
                    if a.is_valid_APK():
        		#TODO: the idea is to add DalvikVM loading code here too as it's taking a lot of time to parse it in each module that use it.
	                self.apk = a
                        self.manifest = self.apk.get_android_manifest_xml().getElementsByTagName("manifest")[0]
			setattr(self.apk, 'dalvik_vm_format', dvm.DalvikVMFormat(self.apk.get_dex()))
		        setattr(self.apk, 'vm_analysis', VMAnalysis(self.apk.dalvik_vm_format))
		        self.apk.dalvik_vm_format.set_vmanalysis(self.apk.vm_analysis)
			self.apk.dalvik_vm_format.create_python_export()
		        gx = GVMAnalysis(self.apk.vm_analysis, None)
        		self.apk.dalvik_vm_format.set_gvmanalysis(gx)
		        self.apk.dalvik_vm_format.create_xref()
                    else:
                        self.error("The APK file you provided is not valid.")
                else:
                    self.error("The APK file you provided is not valid.")
        except Exception as e:
            self.error(str(e))

    def report(self, fmt="json"):
        """Save analysis results as JSON data in analysis directory.
        Params:
        Returns:
        Throws:
        """
        if fmt == "json":
            with open("%s/analysis/%s.json" %
                              (self.root_dir, self.apk.get_package()), "wb") as f:
                f.write(json.dumps(self.analysis))
        elif fmt == "html":
            def path_to_dict(path):
                d = {'name': os.path.basename(path)}
                if os.path.isdir(path):
                    d['type'] = "directory"
                    d['id'] = path
                    d['name'] = os.path.basename(path)
                    d['type'] = "dir"
                    d['children'] = [path_to_dict(os.path.join(path, x)) for x in os.listdir(path)]
                else:
                    d['id'] = path
                    d['name'] = os.path.basename(path)
                    d['url'] = "file://%s" % os.path.abspath(path)
                    d['type'] = "file"
                return d

            logcat = ""
            if os.path.exists("%s/analysis/%s/logs/logcat_full.log" % (self.root_dir, self.apk.get_package())):
                with open("%s/analysis/%s/logs/logcat_full.log" %
                        (self.root_dir, self.apk.get_package())) as f:
                    logcat = f.read()

            netcapture = {
                # "IPs":set((p[IP].src, p[IP].dst) for p in PcapReader('../analysis/%s/network/capture.pcap' % sys.argv[1]) if IP in p)
                "IPs": set()
            }

            loader = FileSystemLoader("%s/reporting/templates" % self.root_dir)
            env = Environment(loader=loader)
            internal_storage = json.dumps([
                path_to_dict("%s/analysis/%s/storage/data/data" %
                             (self.root_dir, self.apk.get_package()))])
            external_storage = json.dumps([path_to_dict("%s/analysis/%s/storage/sdcard" %
                                                        (self.root_dir,
                                                         self.apk.get_package()))])
            template = env.get_template("index.html")
            analysis = json.load(open("%s/analysis/%s.json" %
                                      (self.root_dir, self.apk.get_package())))
            network = {"DNS": [], "HTTP": [], "IP": []}
            if os.path.exists("%s/analysis/%s/network/capture.pcap" % (self.root_dir, self.apk.get_package())):
                try:
                    packets = scapy.rdpcap("%s/analysis/%s/network/capture.pcap" %
                                           (self.root_dir, self.apk.get_package()))
                    network["DNS"] = list(
                        set([packet[scapy.DNSQR].qname for packet in packets if packet.haslayer(scapy.DNSQR)]))

                    for p in packets.filter(lambda (s): http.HTTPResponse in s):
                        p.payload[http.HTTPResponse].payload = str(p.payload[http.HTTPResponse].payload).encode('hex')

                    network["HTTP"] = \
                        [
                            {
                                "request": request.payload[http.HTTPRequest],
                                "response": response.payload[http.HTTPResponse]
                            }  
                            for request, response in \
                            zip(
                                packets.filter(lambda (s): http.HTTPRequest in s),
                                packets.filter(lambda (s): http.HTTPResponse in s)
                            )
                        ]
                except Scapy_Exception as e:
                     self.warning(e.message)
            _v = []
            for v in [analysis["modules"][module]["run"]["vulnerabilities"]
                      for module in analysis["modules"] if len(analysis["modules"][module]["run"]["vulnerabilities"])]:
                _v += v
            html_out = template.render(data=analysis, logcat=logcat,
                                       network=network, internal_storage=internal_storage,
                                       external_storage=external_storage,
                                       vulnerabilities=_v,
                                       netcapture=netcapture)

            with codecs.open("%s/analysis/%s/report.html" % (self.root_dir,
                                                             self.apk.get_package()), "w", "utf-8") as f:
                f.write(html_out)
            return
        else:
            raise Exception("Unsupported report format.")

    def fry(self):
        """Unzip apk file, convert dex to jar with dex2jar, convert dex to smali files with baksmali, convert manifest
        from binary to human readable format with xml-apk-parser.
        Store all files in analysis/{apk_package_name}/ directory for the user to inspect.
        Params:
        Returns:
            True if successful, False otherwise
        Throws:
            Exception
        """
        try:
            self.output("Building analysis directory ...")
            if not os.path.exists("%s/analysis" % self.root_dir):
                os.mkdir("%s/analysis" % self.root_dir)
            if not os.path.exists("%s/analysis/%s" %
                    (self.root_dir, self.apk.get_package())):
                os.mkdir("%s/analysis/%s" % (self.root_dir, self.apk.get_package()))

            if not os.path.exists("%s/analysis/%s/code" %
                    (self.root_dir, self.apk.get_package())):
                os.mkdir("%s/analysis/%s/code" % (self.root_dir, self.apk.get_package()))

            for d in ["orig", "smali", "jar", "decompiled", "native"]:
                if not os.path.exists("%s/analysis/%s/code/%s" %
                        (self.root_dir, self.apk.get_package(), d)):
                    os.mkdir("%s/analysis/%s/code/%s" %
                             (self.root_dir, self.apk.get_package(), d))

            self.output("Unzipping APK file ...")
            with ZipFile(self.apk.get_filename()) as zipapk:
                zipapk.extractall("%s/analysis/%s/code/orig" %
                                  (self.root_dir, self.apk.get_package()))

            self.output("Converting DEX to JAR ...")
            p = subprocess.Popen(
                '%s/libs/dex2jar/dex2jar %s/analysis/%s/code/orig/classes.dex '
                '-f -o %s/analysis/%s/code/jar/classes.jar  1>&2' %
                (
                    self.root_dir,
                    self.root_dir,
                    self.apk.get_package(),
                    self.root_dir,
                    self.apk.get_package()
                ),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stderr, stdout = p.communicate()
            if len(stderr):
                self.error(stderr)

            self.output("Converting DEX to SMALI ...")
            p = subprocess.Popen(
                '%s/libs/baksmali %s/analysis/%s/code/orig/classes.dex -o %s/analysis/%s/code/smali 1>&2' %
                (
                    self.root_dir,
                    self.root_dir,
                    self.apk.get_package(),
                    self.root_dir,
                    self.apk.get_package()
                ),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stderr, stdout = p.communicate()
            if len(stderr):
                self.error(stderr)

            self.output("Decompiling JAR file ...")
            p = subprocess.Popen(
                '%s/libs/jd %s/analysis/%s/code/jar/classes.jar -od %s/analysis/%s/code/decompiled 1>&2' %
                (
                    self.root_dir,
                    self.root_dir,
                    self.apk.get_package(),
                    self.root_dir,
                    self.apk.get_package()
                ),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stderr, stdout = p.communicate()
            if len(stderr):
                self.error(stderr)

            self.output("Converting Application Manifest to human readable format ...")
            with open("%s/analysis/%s/code/orig/AndroidManifest.xml" %
                              (self.root_dir, self.apk.get_package()), "w") as f:
                f.write(self.apk.get_android_manifest_xml().toprettyxml().decode('utf-8'))

        except Exception as e:
            self.error(str(e))

    def teleport(self, avd):
        """Copy all application related files from the device to the analysis directory for further analysis.
        """

        if not os.path.exists("%s/analysis/%s" % (self.root_dir, self.apk.get_package())):
            os.mkdir("%s/analysis/%s" % (self.root_dir, self.apk.get_package()))
        if not os.path.exists("%s/analysis/%s/storage" % (
        self.root_dir, self.apk.get_package())):
            os.mkdir("%s/analysis/%s/storage/" % (self.root_dir, self.apk.get_package()))
        if not os.path.exists("%s/analysis/%s/storage/sdcard" %
                (self.root_dir, self.apk.get_package())):
            os.mkdir(
                "%s/analysis/%s/storage/sdcard" % (self.root_dir, self.apk.get_package()))
        if not os.path.exists("%s/analysis/%s/storage/data" %
                (self.root_dir, self.apk.get_package())):
            os.mkdir(
                "%s/analysis/%s/storage/data" % (self.root_dir, self.apk.get_package()))
        if not os.path.exists("%s/analysis/%s/storage/data/data" %
                (self.root_dir, self.apk.get_package())):
            os.mkdir("%s/analysis/%s/storage/data/data" % (
            self.root_dir, self.apk.get_package()))
        if not os.path.exists("%s/analysis/%s/storage/data/data/%s" %
                (self.root_dir, self.apk.get_package(), self.apk.get_package())):
            os.mkdir("%s/analysis/%s/storage/data/data/%s" % (
            self.root_dir, self.apk.get_package(), self.apk.get_package()))
        if not os.path.exists("%s/analysis/%s/storage/data/system" %
                (self.root_dir, self.apk.get_package())):
            os.mkdir("%s/analysis/%s/storage/data/system" % (
            self.root_dir, self.apk.get_package()))

        source = "/data/data/%s" % self.apk.get_package()
        dest = "%s/analysis/%s/storage/data/data/%s/" % \
               (self.root_dir, self.apk.get_package(), self.apk.get_package())
        avd.pull(source, dest)

        # search files owned by the application's user (u0_a46) in the sdcard mount point.
        #1. get application UID
        uid = None
        avd.pull("/data/system/packages.list", "%s/analysis/%s/storage/data/system/" %
                 (self.root_dir, self.apk.get_package()))
        with open("%s/analysis/%s/storage/data/system/packages.list" %
                          (self.root_dir, self.apk.get_package()), "rb") as f:
            for line in f.readlines():
                if line.startswith(self.apk.get_package()):
                    uid = int(line.split(" ")[1])

        if uid is not None:
            self.output("Found application UID : %d" % uid)
            self.output("Searching for files owned by user %d" % uid)
            files = avd.shell("/system/xbin/busybox find /sdcard -type f -user %d" % uid)
            for f in [x for x in files.split("\n") if len(x)]:
                print avd.pull(f, "%s/analysis/%s/storage/sdcard" %
                               (self.root_dir, self.apk.get_package()))
        return

    def find_avd(self):
        try:
            for avd in Android.get_running_devices():
                if int(self.apk.get_min_sdk_version() or 3) <= avd.target <= \
                        int(self.apk.get_target_sdk_version() or 21):
                    return avd

            for avd in Android.get_avds():
                if int(self.apk.get_min_sdk_version() or 3) <= avd.target <= \
                        int(self.apk.get_target_sdk_version() or 21):
                    return avd

            self.alert("AVD not found, searching for targets ...")
            targets = []  # Android.get_targets()
            t = None
            for target in targets:
                if int(self.apk.get_min_sdk_version()) <= target.api_level <= int(self.apk.get_target_sdk_version()):
                    self.alert("Found target : %s - %d" % (target.name, target.api_level))
                    t = target
                    break
            if t is None:
                self.alert("Can't find a target, installing necessary target and ABI (it can take time) ...")
                p = subprocess.Popen(
                    "android update sdk -a -u -t android-%s,sys-img-armeabi-v7a-android-%s" % (
                        self.apk.get_target_sdk_version(),
                        self.apk.get_target_sdk_version()
                    ),
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                p.stdin.write('y')
                stdout, stderr = p.communicate()
                if stderr:
                    raise Exception(stderr)
                else:
                    if "Unknown Host" in stdout:
                        self.error("Missing internet connectivity. Aborting...")
                    else:
                        self.alert("Necessary target installed.")
                        targets = Android.get_targets()
                        targets = Android.get_targets()
                        for target in targets:
                            if int(self.apk.get_min_sdk_version()) <= target.api_level <= \
                                    int(self.apk.get_target_sdk_version()):
                                t = target
                                break
            self.alert(
                "Creating AVD... [%s, %s, %s]" % (Android.get_devices()[0].id, t.api_level, t.skins.split(",")[0]))
            name = ''.join(
                random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))
            while name in [avd.name for avd in Android.get_avds()]:
                name = ''.join(
                    random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))
            if t.tag_abis is not None:
                return AVD.create(name, t.id, Android.get_devices()[0].id, tag_abi=t.tag_abis[0], sdcard="512M")
            else:
                return AVD.create(name, t.id, Android.get_devices()[0].id, sdcard="512M")
        except Exception as e:
            self.error(str(e))

    def load_modules(self):
        for dirpath, dirnames, filenames in os.walk('./modules/'):
            # remove hidden files and directories
            filenames = [f for f in filenames if not f[0] == '.']
            dirnames[:] = [d for d in dirnames if not d[0] == '.']
            if len(filenames) > 0:
                mod_category = re.search('/modules/([^/]*)', dirpath)
                if not mod_category in self.loaded_category: self.loaded_category[mod_category] = []
                for filename in [f for f in filenames if f.endswith('.py')]:
                    mod_name = filename.split('.')[0]
                    mod_dispname = '%s%s%s' % (
                        self.module_delimiter.join(re.split('/modules/', dirpath)[-1].split('/')),
                        self.module_delimiter,
                        mod_name)
                    mod_loadname = mod_dispname.replace(self.module_delimiter, '_')
                    mod_loadpath = os.path.join(dirpath, filename)
                    mod_file = open(mod_loadpath, 'rb')
                    try:
                        imp.load_source(mod_loadname, mod_loadpath, mod_file)
                        __import__(mod_loadname)
                        self.loaded_category[mod_category].append(mod_loadname)
                        self.loaded_modules[mod_dispname] = mod_loadname
                    except ImportError:
                        print '-' * 60
                        traceback.print_exc()
                        print '-' * 60
                        self.error('Unable to load module: %s' % (mod_name))

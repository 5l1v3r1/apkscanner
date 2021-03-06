# coding=utf-8
import framework

import os
import string
import codecs
import re


class Module(framework.module):
    def __init__(self, apk, avd):
        super(Module, self).__init__(apk, avd)
        self.info = {
            "Name": "Obfuscation detector",
            "Author": "Quentin Kaiser (@QKaiser)",
            "Description": "This module will detect if the application code has been obfuscated with tools like "
                           "Proguard, DexGuard or APKProtect.",
            "Comments": []
        }



    def module_run(self, verbose=False):

        #proguard detection
        proguard = False
        for root, dirs, files in os.walk("%s/analysis/%s/code/decompiled/%s" % (
                self.root_dir,
                self.apk.get_package(),
                "/".join(self.apk.get_package().split("."))
        )):
            for f in files:
                if f in ["%s.java" % x for x in string.ascii_lowercase]:
                    proguard = True

        #dexguard detection

        #1. use of unicode/chinese characters
        chinese_filenames = 0
        for root, dirs, files in os.walk("%s/analysis/%s/smali" % (self.root_dir, self.apk.get_package())):
            for f in files:
                for c in f:
                    if u'\u4e00' <= c <= u'\u9fff':
                        chinese_filenames += 1

        chinese_chars = 0
        for root, dirs, files in os.walk("%s/analysis/%s/smali" % (self.root_dir, self.apk.get_package())):
            for filename in files:
                with codecs.open(os.path.join(root, filename), "rb", "utf-8") as f:
                    for c in f.read():
                        if u'\u4e00' <= c <= u'\u9fff':
                            chinese_chars += 1

        #2. Usage of huge arrays (> 1900 bytes)
        huge_arrays = 0
        for root, dirs, files in os.walk("%s/analysis/%s/smali" % (self.root_dir, self.apk.get_package())):
            for filename in files:
                with open(os.path.join(root, filename), 'rb') as f:
                    matches = re.findall(r'new-array ([^,]*),([^,]*),([^\n]*)\n', f.read())
                    if len(matches):
                        if matches[0][1] > 1900:
                            huge_arrays += 1

        #3. Heavy use of reflection
        reflection = 0
        for root, dirs, files in os.walk("%s/analysis/%s/smali" % (self.root_dir, self.apk.get_package())):
            for filename in files:
                with open(os.path.join(root, filename), 'rb') as f:
                    matches = re.findall('r(Ljava/lang/reflect/[^;];)', f.read())
                    reflection += len(matches)

        #4. Dynamic Code Loading and Executing
        dexclassloader = 0
        for root, dirs, files in os.walk("%s/analysis/%s/smali" % (self.root_dir, self.apk.get_package())):
            for filename in files:
                with open(os.path.join(root, filename), 'rb') as f:
                    matches = re.findall('r(Ldalvik/system/DexClassLoader;)', f.read())
                    dexclassloader += len(matches)

        #5. Heavy use of Java’s encryption classes

        #APKProtect detection
        # The string "APKProtected" is present in the dex
        apkprotect = False
        for root, dirs, files in os.walk("%s/analysis/%s/smali" % (self.root_dir, self.apk.get_package())):
            for filename in files:
                with open(os.path.join(root, filename), 'rb') as f:
                    if "APKProtected" in f.read():
                        apkprotect = True

        dexguard = (dexclassloader > 0 and chinese_chars > 0 and chinese_filenames > 0)

        obfuscator = None
        if dexguard:
            obfuscator = "Dexguard"
        if proguard:
            obfuscator = "Proguard"
        if apkprotect:
            obfuscator = "APKProtect"


        if verbose and obfuscator is not None:
            print "Obfuscator : %s" % obfuscator

        return {
            "results": obfuscator,
            "logs": "",
            "vulnerabilities": [framework.Vulnerability(
                "Lack of Code Obfuscation",
                "Obfuscation raise the bar for third parties that would want to determine how your application is "
                "working and protect your application against piracy or unwanted clones on the market."
                "Multiple solutions exists but we recommend you to use Proguard as it is well integrated into the "
                "Android Studio IDE.",
                framework.Vulnerability.LOW
            ).__dict__] if obfuscator is None else []
        }
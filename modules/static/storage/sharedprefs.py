import framework

from androguard.core.bytecodes import dvm
from androguard.core.analysis.analysis import *
from androguard.decompiler.dad import decompile


class Module(framework.module):

    def __init__(self, apk, avd):
        framework.module.__init__(self, apk, avd)
        self.info = {
            'Name': 'Application shared preferences checker',
            'Author': 'Quentin Kaiser (@QKaiser)',
            'Description': 'blahblah',
            'Comments': []
        }

    def module_run(self):

        logs = ""
        vulnerabilities = []
        results = []

        d = dvm.DalvikVMFormat(self.apk.get_dex())
        dx = VMAnalysis(d)
        z = dx.tainted_packages.search_methods(".", "getSharedPreferences", ".")

        for p in z:
            method = d.get_method_by_idx(p.get_src_idx())
            if method.get_code() is None:
                continue
            mx = dx.get_method(method)
            if self.apk.get_package() in method.get_class_name().replace("/", "."):
                ms = decompile.DvMethod(mx)
                ms.process()
                results.append({
                    "file": method.get_class_name()[1:-1],
                    "line": method.get_debug().get_line_start(),
                    "source": ms.get_source()
                })

        return {
            "results": results,
            "logs": logs,
            "vulnerabilities": vulnerabilities
        }
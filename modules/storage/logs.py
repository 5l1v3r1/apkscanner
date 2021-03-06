import framework

from androguard.core.bytecodes import dvm
from androguard.core.analysis.analysis import *
from androguard.decompiler.dad import decompile

import re


class Module(framework.module):
    def __init__(self, apk, avd):
        super(Module, self).__init__(apk, avd)
        self.info = {
            "Name": "Logging analyzer",
            "Author": "Quentin Kaiser (@QKaiser)",
            "Description": "This modules extracts calls to the Android logger to obtain information being logged from"
                           "a static analysis point of view.",
            "Comments": []
        }

    def module_run(self, verbose=False):

        results = {}

        z = self.apk.vm_analysis.tainted_packages.search_packages("Log")
        for p in z:
            method = self.apk.dalvik_vm_format.get_method_by_idx(p.get_src_idx())
            if self.apk.package.replace(".", "/") in method.get_class_name()[1:-1]:
                if method.get_code() is None:
                    continue
                mx = self.apk.vm_analysis.get_method(method)
                ms = decompile.DvMethod(mx)
                try:
                    ms.process()
                except AttributeError as e:
                    self.warning("Error while processing disassembled Dalvik method: %s" % e.message)
                if method.get_class_name()[1:-1] not in results:
                    results[method.get_class_name()[1:-1]] = []

                if method.get_debug().get_line_start() not in \
                        [x["line"] for x in results[method.get_class_name()[1:-1]]]:
                    results[method.get_class_name()[1:-1]].append(
                        {
                            "type": ms.type,
                            "line": method.get_debug().get_line_start()
                        }
                    )


        return {
            "results": results,
            "vulnerabilities": []
        }

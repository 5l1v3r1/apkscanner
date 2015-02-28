import framework

actions = [
    "android.intent.action.MAIN",
    "android.intent.action.VIEW",
    "android.intent.action.ATTACH_DATA",
    "android.intent.action.EDIT",
    "android.intent.action.INSERT_OR_EDIT",
    "android.intent.action.PICK",
    "android.intent.action.CREATE_SHORTCUT",
    "android.intent.action.CHOOSER",
    "android.intent.action.GET_CONTENT",
    "android.intent.action.DIAL",
    "android.intent.action.CALL",
    "android.intent.action.CALL_EMERGENCY",
    "android.intent.action.CALL_PRIVILEGED",
    "android.intent.action.SENDTO",
    "android.intent.action.SEND",
    "android.intent.action.SEND_MULTIPLE",
    "android.intent.action.ANSWER",
    "android.intent.action.INSERT",
    "android.intent.action.DELETE",
    "android.intent.action.RUN",
    "android.intent.action.SYNC",
    "android.intent.action.PICK_ACTIVITY",
    "android.intent.action.SEARCH",
    "android.intent.action.SYSTEM_TUTORIAL",
    "android.intent.action.WEB_SEARCH",
    "android.intent.action.ALL_APPS"
    "android.intent.action.SET_WALLPAPER",
    "android.intent.action.BUG_REPORT",
    "android.intent.action.FACTORY_TEST",
    "android.intent.action.CALL_BUTTON",
    "android.intent.action.VOICE_COMMAND",
    "android.intent.action.SEARCH_LONG_PRESS",
    "android.intent.action.APP_ERROR",
    "android.intent.action.POWER_USAGE_SUMARY",
    "android.intent.action.UPGRADE_SETUP",
    "android.intent.action.SCREEN_OFF",
    "android.intent.action.SCREEN_ON",
    "android.intent.action.USER_PRESENT",
    "android.intent.action.TIME_TICK",
    "android.intent.action.TIME_SET",
    "android.intent.action.DATE_CHANGED",
    "android.intent.action.TIMEZONE_CHANGED",
    "android.intent.action.ALARM_CHANGED",
    "android.intent.action.SYNC_STATE_CHANGED",
    "android.intent.action.BOOT_COMPLETED",
    "android.intent.action.CLOSE_SYSTEM_DIALOGS",
    "android.intent.action.PACKAGE_INSTALL",
    "android.intent.action.PACKAGE_ADDED",
    "android.intent.action.PACKAGE_REPLACED",
    "android.intent.action.PACKAGE_REMOVED",
    "android.intent.action.PACKAGE_CHANGED",
    "android.intent.action.QUERY_PACKAGE_RESTART",
    "android.intent.action.PACKAGE_RESTARTED",
    "android.intent.action.PACKAGE_DATA_CLEARED",
    "android.intent.action.UID_REMOVED",
    "android.intent.action.EXTERNAL_APPLICATIONS_AVAILABLE",
    "android.intent.action.EXTERNAL_APPLICATIONS_UNAVAILABLE",
    "android.intent.action.WALLPAPER_CHANGED",
    "android.intent.action.CONFIGURATION_CHANGED",
    "android.intent.action.LOCALE_CHANGED",
    "android.intent.action.BATTERY_CHANGED",
    "android.intent.action.BATTERY_LOW",
    "android.intent.action.BATTERY_OKAY",
    "android.intent.action.ACTION_POWER_CONNECTED",
    "android.intent.action.ACTION_POWER_DISCONNECTED",
    "android.intent.action.ACTION_SHUTDOWN",
    "android.intent.action.ACTION_REQUEST_SHUTDOWN",
    "android.intent.action.DEVICE_STORAGE_LOW",
    "android.intent.action.DEVICE_STORAGE_OK",
    "android.intent.action.MANAGE_PACKAGE_STORAGE",
    "android.intent.action.UMS_CONNECTED",
    "android.intent.action.UMS_DISCONNECTED",
    "android.intent.action.MEDIA_REMOVED",
    "android.intent.action.MEDIA_UNMOUNTED",
    "android.intent.action.MEDIA_CHECKING",
    "android.intent.action.MEDIA_NOFS",
    "android.intent.action.MEDIA_MOUNTED",
    "android.intent.action.MEDIA_SHARED",
    "android.intent.action.MEDIA_UNSHARED",
    "android.intent.action.MEDIA_BAD_REMOVAL",
    "android.intent.action.MEDIA_UNMOUNTABLE",
    "android.intent.action.MEDIA_EJECT",
    "android.intent.action.MEDIA_SCANNER_STARTED",
    "android.intent.action.MEDIA_SCANNER_FINISHED",
    "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
    "android.intent.action.MEDIA_BUTTON",
    "android.intent.action.CAMERA_BUTTON",
    "android.intent.action.GTALK_CONNECTED",
    "android.intent.action.GTALK_DISCONNECTED",
    "android.intent.action.INPUT_METHOD_CHANGED",
    "android.intent.action.AIRPLANE_MODE",
    "android.intent.action.PROVIDER_CHANGED",
    "android.intent.action.HEADSET_PLUG",
    "android.intent.action.NEW_OUTGOING_CALL",
    "android.intent.action.REBOOT",
    "android.intent.action.DOCK_EVENT",
    "android.intent.action.PRE_BOOT_COMPLETED"
]

extras = [
    "android.intent.extra.shortcut.INTENT",
    "android.intent.extra.shortcut.NAME",
    "android.intent.extra.shortcut.ICON",
    "android.intent.extra.shortcut.ICON_RESOURCE",
    "android.intent.extra.TEMPLATE",
    "android.intent.extra.TEXT",
    "android.intent.extra.STREAM",
    "android.intent.extra.EMAIL",
    "android.intent.extra.CC",
    "android.intent.extra.BCC",
    "android.intent.extra.SUBJECT",
    "android.intent.extra.INTENT",
    "android.intent.extra.TITLE",
    "android.intent.extra.INITIAL_INTENTS",
    "android.intent.extra.KEY_EVENT",
    "android.intent.extra.KEY_CONFIRM",
    "android.intent.extra.DONT_KILL_APP",
    "android.intent.extra.PHONE_NUMBER",
    "android.intent.extra.UID",
    "android.intent.extra.PACKAGES",
    "android.intent.extra.DATA_REMOVED",
    "android.intent.extra.REPLACING",
    "android.intent.extra.ALARM_COUNT",
    "android.intent.extra.DOCK_STATE",
    "android.intent.extra.BUG_REPORT",
    "android.intent.extra.INSTALLER_PACKAGE_NAME"
]

categories = [
    "android.intent.category.DEFAULT",
    "android.intent.category.BROWSABLE",
    "android.intent.category.ALTERNATIVE",
    "android.intent.category.SELECTED_ALTERNATIVE",
    "android.intent.category.TAB",
    "android.intent.category.LAUNCHER",
    "android.intent.category.INFO",
    "android.intent.category.HOME",
    "android.intent.category.PREFERENCE",
    "android.intent.category.DEVELOPMENT_PREFERENCE",
    "android.intent.category.EMBED",
    "android.intent.category.MONKEY",
    "android.intent.category.TEST",
    "android.intent.category.UNIT_TEST",
    "android.intent.category.SAMPLE_CODE",
    "android.intent.category.OPENABLE",
    "android.intent.category.FRAMEWORK_INSTRUMENTATION_TEST",
    "android.intent.category.CAR_DOCK",
    "android.intent.category.DESK_DOCK",
    "android.intent.category.CAR_MODE",
]


#TODO: fix key transmission fuzzing
class Module(framework.module):
    def __init__(self, apk, avd):
        super(Module, self).__init__(apk, avd)
        self.info = {
            'Name': 'Unprotected broadcast receivers.',
            'Author': 'Quentin Kaiser (@QKaiser)',
            'Description': '',
            'Comments': []
        }

    def module_run(self, verbose=False):
        logs = ""
        vulnerabilities = []
        receivers = self.get_receivers()

        #for each action by categories, send intent and see what happen
        for receiver in receivers:
            receiver["vulnerable"] = False
            if receiver["exported"] and receiver["permission"] is None:
                #1. Get exposed broadcast receivers from results
                for intent in receiver["intent_filters"]:
                    if intent['category'] is not None:
                        output = self.avd.shell("am broadcast -a %s -c %s -n %s/%s" %
                                                (intent['action'], intent['category'],
                                                 self.apk.get_package(), receiver["name"]))
                    else:
                        output = self.avd.shell("am broadcast -a %s -n %s/%s" %
                                                (intent['action'], self.apk.get_package(), receiver["name"]))

                    if "Broadcast completed" not in output:

                        logs += "$ adb shell am broadcast -a %s -c %s -n %s/%s\n%s\n" % \
                                (intent['action'], category, self.apk.get_package(), receiver["name"], output)
                        receiver["vulnerable"] = True
                        vulnerabilities.append(
                            framework.Vulnerability("Unprotected broadcast receiver.",
                                            "The following broadcast receivers were found to be vulnerable.",
                                            framework.Vulnerability.LOW).__dict__
                        )

                if not len(receiver["intent_filters"]):
                    for category in categories:
                        for action in actions:
                            #2. Fuzz receivers with a set of intents (Null intents, malformed, ...)
                            output = self.avd.shell("am broadcast -a %s -c %s -n %s/%s" %
                                                    (action, category, self.apk.get_package(), receiver["name"]))
                            if "Broadcast completed" not in output:
                                print output
                                logs += "$ adb shell am broadcast -a %s -c %s -n %s/%s\n%s\n" % \
                                        (action, category, self.apk.get_package(), receiver["name"], output)
                                receiver["vulnerable"] = True
                                vulnerabilities.append(
                                    framework.Vulnerability("Unprotected broadcast receiver.",
                                                    "The following broadcast receivers were found to be vulnerable.",
                                                    framework.Vulnerability.LOW).__dict__
                                )

        return {
            "results": receivers,
            "logs": logs,
            "vulnerabilities": vulnerabilities
        }
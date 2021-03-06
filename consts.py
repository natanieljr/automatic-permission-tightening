# Command line parameters (configuration)
ARG_APK = '--apk'
ARG_APK_SHORT = '-a'
ARG_DIR = '--directory'
ARG_DIR_SHORT = '-d'
ARG_OUT = '--output'
ARG_OUT_SHORT = '-o'
ARG_TMP = '--tmpDir'
ARG_TMP_SHORT = '-t'

# Command line parameters (actions)
ARG_KEEP_DIR = '--keepDirectories'
ARG_KEEP_DIR_NO = '--no-keepDirectories'
ARG_CFG = '--extractConfig'
ARG_CFG_NO = '--no-extractConfig'
ARG_INLINE = '--inline'
ARG_INLINE_NO = '--no-inline'
ARG_EXPLORE = '--explore'
ARG_EXPLORE_NO = '--no-explore'
ARG_EXTRACT_APIS = '--extractAPIs'
ARG_EXTRACT_APIS_NO = '--no-extractAPIs'
ARG_GENERATE_SCENARIOS = '--generateScenarios'
ARG_GENERATE_SCENARIOS_NO = '--no-generateScenarios'
ARG_RUN_SCENARIOS = '--runScenarios'
ARG_RUN_SCENARIOS_NO = '--no-runScenarios'
ARG_APP_CRASH = '--use-appCrashed'
ARG_APP_CRASH_NO = '--no-use-appCrashed'
ARG_OBS_EXPL = '--use-obsExpl'
ARG_OBS_EXPL_NO = '--no-use-obsExpl'
ARG_RUN_SCENARIOS_COMP = '--runScenariosComp'
ARG_RUN_SCENARIOS_COMP_NO = '--no-runScenariosComp'


# ADB commands
ADB_INSTALL_COMMAND = "adb install %s"
ADB_EXPORT_COMMAND = "adb shell am start -a biz.bokhorst.xprivacy.action.EXPORT -e FileName '/storage/emulated/0/.xprivacy/%s.xml'"
ADB_PULL_COMMAND = "adb pull /storage/emulated/0/.xprivacy/%s.xml %s/%s.xml"
ADB_UNINSTALL_COMMAND = 'adb uninstall %s'
ADB_REBOOT_COMMAND = 'adb reboot'
ADB_UNLOCK_SCREEN_COMMAND = 'adb shell input keyevent 82'
# Returns Parcel(00000000 00000000) if locked and Parcel(00000000 00000001) if unlocked
ADB_CHECK_LOCKED_SCREEN_COMMAND = 'adb shell service call power 12'
ADB_REMOVE_CONFIG = "adb shell 'rm /storage/emulated/0/.xprivacy/xPrivacyConfig.xml'"

# XPrivacy enabler/disabler
XPRIVACY_ENABLER_BASE = 'resources\\xprivacy_enabler_base.apk'
XPRIVACY_ENABLER_TEST = 'resources\\xprivacy_enabler_base.apk'
XPRIVACY_ENABLER_RUN = 'adb shell am instrument -w -r -e enable %s -e debug true -e class org.droidmate.mockable.xprivacy.XPrivacyEnabler#init org.droidmate.mockable.xprivacy.xprivacyenabler.test/android.support.test.runner.AndroidJUnitRunner'

# Droidmate commands
JDK_LOCATION = "C:\\Program Files\\Java\\jdk1.8.0_45"
DROIDMATE_LOCATION = "C:\\Users\\natan_000\\Desktop\\Saarland\\repositories\\droidmate"
GRADLE_CACHE = "C:\\Users\\natan_000\\.gradle\\caches"
DROIDMATE_BASE = ['"<JDK>\\bin\\java" '.replace("<JDK>", JDK_LOCATION), 
                  '-ea '
                  '-Didea.launcher.port=7532 ' 
                  '"-Didea.launcher.bin.path=C:\\Program Files (x86)\\JetBrains\\IntelliJ IDEA 2016.2.1\\bin" ' 
                  '-Dfile.encoding=UTF-8 ' 
                  '-classpath ' 
                  '"<JDK>\\jre\\lib\\charsets.jar;'
                  '<JDK>\\jre\\lib\\deploy.jar;'
                  '<JDK>\\jre\\lib\\ext\\access-bridge-64.jar;'
                  '<JDK>\\jre\\lib\\ext\\cldrdata.jar;'
                  '<JDK>\\jre\\lib\\ext\\dnsns.jar;'
                  '<JDK>\\jre\\lib\\ext\\jaccess.jar;'
                  '<JDK>\\jre\\lib\\ext\\jfxrt.jar;'
                  '<JDK>\\jre\\lib\\ext\\localedata.jar;'
                  '<JDK>\\jre\\lib\\ext\\nashorn.jar;'
                  '<JDK>\\jre\\lib\\ext\\sunec.jar;'
                  '<JDK>\\jre\\lib\\ext\\sunjce_provider.jar;'
                  '<JDK>\\jre\\lib\\ext\\sunmscapi.jar;'
                  '<JDK>\\jre\\lib\\ext\\sunpkcs11.jar;'
                  '<JDK>\\jre\\lib\\ext\\zipfs.jar;'
                  '<JDK>\\jre\\lib\\javaws.jar;'
                  '<JDK>\\jre\\lib\\jce.jar;'
                  '<JDK>\\jre\\lib\\jfr.jar;'
                  '<JDK>\\jre\\lib\\jfxswt.jar;'
                  '<JDK>\\jre\\lib\\jsse.jar;'
                  '<JDK>\\jre\\lib\\management-agent.jar;'
                  '<JDK>\\jre\\lib\\plugin.jar;'
                  '<JDK>\\jre\\lib\\resources.jar;'
                  '<JDK>\\jre\\lib\\rt.jar;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\command\\build\\classes\\main;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\core\\build\\classes\\main;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\core\\build\\resources\\main;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\reporter\\build\\classes\\main;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\reporter\\build\\resources\\main;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\lib-kotlin\\build\\classes\\main;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\lib-common\\build\\classes\\main;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\lib-common\\build\\resources\\main;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\apk-inliner\\build\\classes\\main;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\apk-inliner\\build\\resources\\main;'
                  '<GRADLE>\\modules-2\\files-2.1\\com.github.konrad-jamrozik\\utilities\\f7e0d5d163\\67c0a10a2848fefe75784072160e0aa338400e72\\utilities-f7e0d5d163.jar;'
                  '<DROIDMATE>\\dev\\droidmate\\projects\\uiautomator-daemon-lib\\build\\classes\\main;'
                  '<GRADLE>\\modules-2\\files-2.1\\com.beust\\jcommander\\1.35\\47592e181b0bdbbeb63029e08c5e74f6803c4edd\\jcommander-1.35.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\com.google.guava\\guava\\19.0\\6ce200f6b23222af3d8abb6b6459e6c44f4bb0e9\\guava-19.0.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.apache.commons\\commons-lang3\\3.3\\5ccde9cb5e3071eaadf5d87a84b4d0aba43b119\\commons-lang3-3.3.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\commons-io\\commons-io\\2.4\\b1b6ea3b7e4aa4f492509a4952029cd8e48019ad\\commons-io-2.4.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.apache.commons\\commons-exec\\1.2\\635b879f2ab19834f56b98bd0a532d8f029d0588\\commons-exec-1.2.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.codehaus.groovy\\groovy-all\\2.4.6\\478feadca929a946b2f1fb962bb2179264759821\\groovy-all-2.4.6.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\ch.qos.logback\\logback-classic\\1.0.13\\6b56ec752b42ccfa1415c0361fb54b1ed7ca3db6\\logback-classic-1.0.13.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\ch.qos.logback\\logback-core\\1.0.13\\dc6e6ce937347bd4d990fc89f4ceb469db53e45e\\logback-core-1.0.13.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\net.sf.opencsv\\opencsv\\2.3\\c23708cdb9e80a144db433e23344a788a1fd6599\\opencsv-2.3.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.graphstream\\gs-core\\1.3\\1199c349ae387742426ee216bcebcc0b5a51b2fa\\gs-core-1.3.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\com.google.jimfs\\jimfs\\1.0\\edd65a2b792755f58f11134e76485a928aab4c97\\jimfs-1.0.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.jetbrains.kotlin\\kotlin-stdlib\\1.0.3\\20738122b53399036c321eeb84687367757d622a\\kotlin-stdlib-1.0.3.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.jetbrains.kotlin\\kotlin-reflect\\1.0.3\\ed9cbaeb8dccd2027348185044012aac145a5c61\\kotlin-reflect-1.0.3.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.zeroturnaround\\zt-exec\\1.9\\a6c5747098b1ede9f4a6e9c36eaebb357a4430ed\\zt-exec-1.9.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\net.sf.jopt-simple\\jopt-simple\\4.9\\ee9e9eaa0a35360dcfeac129ff4923215fd65904\\jopt-simple-4.9.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\junit\\junit\\4.12\\2973d150c0dc1fefe998f834810d68f278ea58ec\\junit-4.12.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.graphstream\\pherd\\1.0\\def146e11a24b48f88e8af5fa14ca383f8ee4dd2\\pherd-1.0.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.graphstream\\mbox2\\1.0\\c20049788c1bde824e17cd8e26c2f515a1eab352\\mbox2-1.0.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.jetbrains.kotlin\\kotlin-runtime\\1.0.3\\10f40d016700cf4287e49fa1d51c2a8507e9b946\\kotlin-runtime-1.0.3.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.hamcrest\\hamcrest-core\\1.3\\42a25dc3219429f0e5d060061f71acb49bf010a0\\hamcrest-core-1.3.jar;'
                  '<GRADLE>\\modules-2\\files-2.1\\org.slf4j\\slf4j-api\\1.7.20\\867d63093eff0a0cb527bf13d397d850af3dcae3\\slf4j-api-1.7.20.jar;'
                  'C:\\Program Files (x86)\\JetBrains\\IntelliJ IDEA 2016.2.1\\lib\\idea_rt.jar"'
                  'com.intellij.rt.execution.application.AppMain '
                  'org.droidmate.frontend.DroidmateFrontend'
                      .replace("<JDK>", JDK_LOCATION)
                      .replace("<DROIDMATE>", DROIDMATE_LOCATION)
                      .replace("<GRADLE>", GRADLE_CACHE)
                  ]

DROIDMATE_INLINE_APK = [DROIDMATE_BASE[0], DROIDMATE_BASE[1] + ' -inline -apksDir=%s']
#DROIDMATE_FIRST_RUN = [DROIDMATE_BASE[0], DROIDMATE_BASE[1] + ' -apksDir=%s -resetEvery=30 -timeLimit=10 -randomSeed=0 -getValidGuiSnapshotRetryAttempts=2 -androidApi=api23']
DROIDMATE_FIRST_RUN = [DROIDMATE_BASE[0], DROIDMATE_BASE[1] + ' -apksDir=%s -resetEvery=30 -timeLimit=120 -randomSeed=0 -getValidGuiSnapshotRetryAttempts=2 -androidApi=api23']
#DROIDMATE_FIRST_RUN = [DROIDMATE_BASE[0], DROIDMATE_BASE[1] + ' -apksDir=%s -resetEvery=30 -timeLimit=900 -randomSeed=0 -getValidGuiSnapshotRetryAttempts=2 -androidApi=api23']
DROIDMATE_RUN_WITH_XPRIVACY = [DROIDMATE_FIRST_RUN[0], DROIDMATE_FIRST_RUN[1] + ' -xPrivacyConfigurationFile=%s']

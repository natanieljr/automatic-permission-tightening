import logging
import os
from apk_parse.apk import APK, ZIPMODULE

logger = logging.getLogger()


class APKAdapter(APK):
    def __init__(self, filename, raw=False, mode="r", magic_file=None, zipmodule=ZIPMODULE):
        APK.__init__(self, filename, raw, mode, magic_file, zipmodule)

        if self.package == "":
            logger.warn("Couldn't extract package name and version from APK. Using heuristic")
            file_name = os.path.splitext(os.path.basename(self.filename))[0]
            data = file_name.split('_')

            if len(data) == 2:
                package_name = data[0]
                version = data[1].replace('v', '').replace('_', '.')
                self.package = package_name
                self.androidversion["Name"] = version
                logger.warn("Heuristic identified: %s", self)

    def __str__(self):
        if self.package == "":
            return self.filename

        return "package=%s, version=%s" % (self.package, self.get_androidversion_name())

    def get_basename(self):
        return os.path.basename(self.filename)

    def get_dirname(self):
        return os.path.dirname(self.filename)

    def get_apk_name_as_directory_name(self):
        if self.package == "":
            data = self.filename.replace('.apk', '')
        else:
            data = '%s_v%s' % (self.package, self.get_androidversion_name().replace('.', '_'))

        if '(' in data:
            start = data.index('(')
            end = data.index(')')
            data = data[:start - 1] + data[end + 1:]

        return data
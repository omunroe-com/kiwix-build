from .base import (
    Dependency,
    SvnClone,
    MakeBuilder
)

from kiwixbuild.utils import SkipCommand
from kiwixbuild._global import get_target_step

class Icu(Dependency):
    name = "icu4c"

    class Source(SvnClone):
        name = "icu4c"
        svn_remote = "http://source.icu-project.org/repos/icu/tags/release-58-2/icu4c"
        svn_dir = "icu4c"

        patches = ["icu4c_fix_static_lib_name_mingw.patch",
                   "icu4c_android_elf64_st_info.patch",
                   "icu4c_custom_data.patch",
                   "icu4c_noxlocale.patch",
                   "icu4c_rpath.patch"]


    class Builder(MakeBuilder):
        subsource_dir = "source"

        @property
        def configure_option(self):
            options = "--disable-samples --disable-tests --disable-extras --disable-dyload --enable-rpath"
            if self.buildEnv.platformInfo.build == 'android':
                options += " --with-data-packaging=archive"
            return options


class Icu_native(Icu):
    name = "icu4c_native"
    force_native_build = True

    class Builder(Icu.Builder):
        @property
        def build_path(self):
            return super().build_path+"_native"

        def _install(self, context):
            raise SkipCommand()


class Icu_cross_compile(Icu):
    name = "icu4c_cross-compile"

    class Builder(Icu.Builder):
        dependencies = ['icu4c_native']

        @property
        def configure_option(self):
            icu_native_builder = get_target_step('icu4c_native', self.buildEnv.platformInfo.name)
            return (super().configure_option
                  + " --with-cross-build={} --disable-tools"
                  ).format(icu_native_builder.build_path)

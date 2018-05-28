
import subprocess

from .base import PlatformInfo
from kiwixbuild.utils import pj, xrun_find


class iOSPlatformInfo(PlatformInfo):
    build = 'iOS'
    static = True
    compatible_hosts = ['Darwin']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._root_path = None

    @property
    def root_path(self):
        if self._root_path is None:
            command = "xcodebuild -version -sdk {} | grep -E '^Path' | sed 's/Path: //'".format(self.sdk_name)
            self._root_path = subprocess.check_output(command, shell=True)[:-1].decode()
        return self._root_path

    def __str__(self):
        return "iOS"

    def finalize_setup(self):
        super().finalize_setup()
        self.buildEnv.cmake_crossfile = self._gen_crossfile('cmake_ios_cross_file.txt')
        self.buildEnv.meson_crossfile = self._gen_crossfile('meson_cross_file.txt')

    def get_cross_config(self):
        return {
            'root_path': self.root_path,
            'binaries': self.binaries,
            'exec_wrapper_def': '',
            'extra_libs': ['-fembed-bitcode', '-isysroot', self.root_path, '-arch', self.arch, '-miphoneos-version-min=9.0', '-stdlib=libc++'],
            'extra_cflags': ['-fembed-bitcode', '-isysroot', self.root_path, '-arch', self.arch, '-miphoneos-version-min=9.0', '-stdlib=libc++'],
            'host_machine': {
                'system': 'Darwin',
                'lsystem': 'darwin',
                'cpu_family': self.arch,
                'cpu': self.cpu,
                'endian': '',
                'abi': ''
            },
        }

    def set_env(self, env):
        env['CFLAGS'] = " -fembed-bitcode -isysroot {SDKROOT} -arch {arch} -miphoneos-version-min=9.0 ".format(SDKROOT=self.root_path, arch=self.arch) + env['CFLAGS']
        env['CXXFLAGS'] = env['CFLAGS'] + " -stdlib=libc++ -std=c++11 "+env['CXXFLAGS']
        env['LDFLAGS'] = " -arch {arch} -isysroot {SDKROOT} ".format(SDKROOT=self.root_path, arch=self.arch)
        env['MACOSX_DEPLOYMENT_TARGET'] = "10.7"

    def get_bin_dir(self):
        return [pj(self.root_path, 'bin')]

    @property
    def binaries(self):
        return {
            'CC': xrun_find('clang'),
            'CXX': xrun_find('clang++'),
            'AR': '/usr/bin/ar',
            'STRIP': '/usr/bin/strip',
            'RANLIB': '/usr/bin/ranlib',
            'LD': '/usr/bin/ld',
        }

    @property
    def configure_option(self):
        return '--host={}'.format(self.arch_full)

    def set_compiler(self, env):
        env['CC'] = self.binaries['CC']
        env['CXX'] = self.binaries['CXX']


class iOSArmv7(iOSPlatformInfo):
    name = 'iOS_armv7'
    arch = cpu = 'armv7'
    arch_full =  'arm-apple-darwin'
    sdk_name = 'iphoneos'

class iOSArm64(iOSPlatformInfo):
    name = 'iOS_arm64'
    arch = cpu = 'arm64'
    arch_full =  'arm-apple-darwin'
    sdk_name = 'iphoneos'

class iOSi386(iOSPlatformInfo):
    name = 'iOS_i386'
    arch = cpu = 'i386'
    arch_full =  ''
    sdk_name = 'iphonesimulator'

class iOSx64(iOSPlatformInfo):
    name = 'iOS_x86_64'
    arch = cpu = 'x86_64'
    arch_full =  ''
    sdk_name = 'iphonesimulator'

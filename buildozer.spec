[app]

title = Nucleus PRL
package.name = nucleusprl
package.domain = com.nucleus.prl

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0.0

requirements = python3,kivy==2.3.0,pyjnius,android

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/logo.png

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 33
android.build_tools_version = 29.0.0
android.minapi = 21
android.ndk = 23b
android.accept_sdk_license = True 
android.ndk_api = 21
android.archs = arm64-v8a
android.allow_backup = True

android.presplash_color = #0A84FF
android.presplash_bg = logo.png

# Android boot splash
android.add_src =

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1

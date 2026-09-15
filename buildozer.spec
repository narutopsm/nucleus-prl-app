[app]

title = Nucleus PRL
package.name = nucleusprl
package.domain = com.nucleus.prl

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf

version = 1.0.0

requirements = python3,kivy==2.3.0,pyjnius

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/logo.png

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.allow_backup = True

android.presplash_color = #0A84FF
android.presplash_bg = logo.png

android.accept_sdk_license = True

p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1

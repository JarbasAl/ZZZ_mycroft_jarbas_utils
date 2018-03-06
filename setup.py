from distutils.core import setup

setup(
    name='mycroft_jarbas_utils',
    version='0.1',
    packages=['mycroft_jarbas_utils', 'mycroft_jarbas_utils.tts', 'mycroft_jarbas_utils.intent', 'mycroft_jarbas_utils.listener',
              'mycroft_jarbas_utils.messagebus'],
    url='https://github.com/JarbasAl/mycroft_jarbas_utils',
    license='MIT',
    author='jarbasAi',
    author_email='jarbasai@mailfence.com',
    description='mycroft dev tools'
)

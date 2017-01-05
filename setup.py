from glob import glob

from pbr import util
from setuptools import setup

cfg = util.cfg_to_args()
cfg.update({
    'data_files': [
        ('docs', glob('docs/*.rst'))
    ],
    # 'pbr': True,

})
setup(
    **cfg
)

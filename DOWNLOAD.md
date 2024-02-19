Dataset **NAO** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/H/j/Sy/wt85EkIHYFmZb7sH9tNks8qI5Q4pEUowQzOU9znyXnVrGW2sKiG0jkQGacVSPWMzoOKshpmThUHwizAG2TiXY5POihme49pT9aiORwePM6kUnzzDZ4DF6ocWHdW0.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='NAO', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](https://drive.google.com/drive/folders/15P8sOWoJku6SSEiHLEts86ORfytGezi8).
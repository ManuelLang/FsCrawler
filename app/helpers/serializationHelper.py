#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

import datetime as dt
import json

from loguru import logger


class DateTimeAwareEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, dt.datetime):
            return o.isoformat().replace('+00:00', '')

        return json.JSONEncoder.default(self, o)


class JsonDumper:

    @staticmethod
    def _dumper(obj):
        if obj is None:
            return 'None'
        if isinstance(obj, dt.datetime):
            return obj.replace(microsecond=0).isoformat().replace('+00:00', '')
        if isinstance(obj, dt.timedelta):
            return str(obj)
        if isinstance(obj, object):
            try:
                return obj.toJSON()
            except:
                try:
                    return obj.to_json()
                except:
                    try:
                        return obj.__dict__
                    except:
                        return str(obj)
        return str(obj)

    @staticmethod
    def dumps(obj, format=True):
        try:
            if format:
                return json.dumps(obj, default=JsonDumper._dumper, sort_keys=True, indent=4)
            else:
                return json.dumps(obj, default=JsonDumper._dumper)
        except Exception as ex:
            logger.error(f"Unable to serialize object: {obj}. Error: {ex}")

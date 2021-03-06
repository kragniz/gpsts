import serial
import time

class AttributeDict(dict):
    """Access elements of the dict as attributes"""
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

def _float_or_none(value):
    """Return None if the input value is empty, else return the value converted
    into a float"""
    if value:
        return float(value)
    else:
        return None

def _parse_time(s):
    return s[:2], s[2:4], s[4:]

class Gps(object):
    """A GPS receiver"""
    def __init__(self):
        self._gpsSerial = serial.Serial('/dev/ttyUSB0', 4800, timeout=0.5)

    def time(self):
        t = 0
        while t == 0:
            time.sleep(0.5)
            try:
                line = self.get_gga_line()
            except IOError:
                print 'GGA couldn\'t be found in time, waiting for a bit then retrying'
            if self.checksum(line):
                fields = self._name_fields(line)
                t = _parse_time(fields.time)
            else:
                print 'Checksum failed, retrying...'
        return t

    def get_gga_line(self, attempts=20):
        for i in range(attempts):
            line = self._gpsSerial.readline(None).strip()
            if line.startswith('$GPGGA'):
                return line
        raise IOError('GPS didn\'t give a gga string in time')

    def checksum(self, line):
        """Return True if the checksum passed"""
        x = 0
        for c in line[1:-3]:
            x ^= ord(c)
        x = str(hex(x))[2:].upper()
        check_digits = line[-2:].upper()
        return check_digits == x

    def _name_fields(self, line):
        """Return an AttributeDict containing the more important GGA fields"""
        fields = line[1:-3].split(',')[:8]
        names = [
                    'id',
                    'time',
                    'lat',
                    'lat_direction',
                    'long',
                    'long_direction',
                    'fix_quality',
                    'satellite_number',
                    'hdop',
                    'altitude'
                ]
        d = AttributeDict()
        for i in range(len(fields)):
            d[names[i]] = fields[i]
        return d

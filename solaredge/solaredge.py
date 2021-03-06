import requests
import functools
import pytz
import dateutil.parser
import datetime as dt

__title__ = "solaredge"
__version__ = "0.0.1"
__author__ = "Bert Outtier"
__license__ = "MIT"

BASEURL = 'https://monitoringapi.solaredge.com'


class Solaredge:
    """
    Object containing SolarEdge's site API-methods.
    See https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf
    """
    def __init__(self, site_token):
        """
        To communicate, you need to set a site token.
        Get it from your account.

        Parameters
        ----------
        site_token : str
        """
        self.token = site_token

    @functools.lru_cache(maxsize=128, typed=False)
    def get_list(self, size=100, start_index=0, search_text="", sort_property="",
                 sort_order='ASC', status='Active,Pending'):
        """
        Request service locations

        Returns
        -------
        dict
        """

        url = urljoin(BASEURL, "sites", "list")

        params = {
            'api_key': self.token,
            'size': size,
            'startIndex': start_index,
            'sortOrder': sort_order,
            'status': status
        }

        if search_text:
            params['searchText'] = search_text

        if sort_property:
            params['sortProperty'] = sort_property

        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    @functools.lru_cache(maxsize=128, typed=False)
    def get_details(self, site_id):
        """
        Request service location info

        Parameters
        ----------
        site_id : int

        Returns
        -------
        dict
        """
        url = urljoin(BASEURL, "site", site_id, "details")
        params = {
            'api_key': self.token
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    @functools.lru_cache(maxsize=128, typed=False)
    def get_data_period(self, site_id):
        """
        Request data period

        Parameters
        ----------
        site_id : int

        Returns
        -------
        dict
        """
        url = urljoin(BASEURL, "site", site_id, "dataPeriod")
        params = {
            'api_key': self.token
        }
        r = requests.get(url, params)
        r.raise_for_status()
        j = r.json()
        return j

    def get_data_period_parsed(self, site_id):
        """
        Get data period, parsed in datetime objects

        Parameters
        ----------
        site_id : int

        Returns
        -------
        (dt.datetime, dt.datetime)
        """
        j = self.get_data_period(site_id=site_id)
        tz = pytz.timezone(self.get_timezone(site_id=site_id))
        start, end = [dateutil.parser.parse(j['dataPeriod'][param]) for param in ['startDate', 'endDate']]
        start, end = start.astimezone(tz), end.astimezone(tz)
        return start, end

    def get_energy(self, site_id, start_date, end_date, time_unit='DAY'):
        url = urljoin(BASEURL, "site", site_id, "energy")
        params = {
            'api_key': self.token,
            'startDate': start_date,
            'endDate': end_date,
            'timeUnit': time_unit
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_time_frame_energy(self, site_id, start_date, end_date, time_unit='DAY'):
        url = urljoin(BASEURL, "site", site_id, "timeFrameEnergy")
        params = {
            'api_key': self.token,
            'startDate': start_date,
            'endDate': end_date,
            'timeUnit': time_unit
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_power(self, site_id, start_time, end_time):
        url = urljoin(BASEURL, "site", site_id, "power")
        params = {
            'api_key': self.token,
            'startTime': start_time,
            'endTime': end_time
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_overview(self, site_id):
        url = urljoin(BASEURL, "site", site_id, "overview")
        params = {
            'api_key': self.token
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_power_details(self, site_id, start_time, end_time, meters=None):
        url = urljoin(BASEURL, "site", site_id, "powerDetails")
        params = {
            'api_key': self.token,
            'startTime': start_time,
            'endTime': end_time
        }

        if meters:
            params['meters'] = meters

        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_energy_details(self, site_id, start_time, end_time, meters=None, time_unit="DAY"):
        url = urljoin(BASEURL, "site", site_id, "energyDetails")
        params = {
            'api_key': self.token,
            'startTime': start_time,
            'endTime': end_time,
            'timeUnit': time_unit
        }

        if meters:
            params['meters'] = meters

        r = requests.get(url, params)
        r.raise_for_status()

        j = r.json()
        return j

    def get_energy_details_dataframe(self, site_id, start_time, end_time, meters=None, time_unit="DAY"):
        from .parsers import parse_energydetails
        tz = self.get_timezone(site_id=site_id)
        start_time, end_time = [self._fmt_date(date_obj=time, fmt='%Y-%m-%d %H:%M:%S', tz=tz) for time in [start_time, end_time]]
        j = self.get_energy_details(site_id=site_id, start_time=start_time, end_time=end_time, meters=meters, time_unit=time_unit)
        df = parse_energydetails(j)
        df = df.tz_localize(tz)
        return df

    def get_current_power_flow(self, site_id):
        url = urljoin(BASEURL, "site", site_id, "currentPowerFlow")
        params = {
            'api_key': self.token
        }

        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_storage_data(self, site_id, start_time, end_time, serials=None):
        url = urljoin(BASEURL, "site", site_id, "storageData")
        params = {
            'api_key': self.token,
            'startTime': start_time,
            'endTime': end_time
        }

        if serials:
            params['serials'] = serials.join(',')

        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_inventory(self, site_id):
        url = urljoin(BASEURL, "site", site_id, "inventory")
        params = {
            'api_key': self.token
        }
        r = requests.get(url, params)
        r.raise_for_status()
        return r.json()

    def get_timezone(self, site_id):
        details = self.get_details(site_id=site_id)
        tz = details['details']['location']['timeZone']
        return tz

    @staticmethod
    def _fmt_date(date_obj, fmt, tz=None):
        """
        Convert any input to a valid datestring of format
        If you pass a localized datetime, it is converted to tz first

        Parameters
        ----------
        date_obj : str | dt.date | dt.datetime

        Returns
        -------
        str
        """
        if isinstance(date_obj, str):
            try:
                dt.datetime.strptime(date_obj, fmt)
            except ValueError:
                date_obj = dateutil.parser.parse(date_obj)
            else:
                return date_obj
        if hasattr(date_obj, 'tzinfo') and date_obj.tzinfo is not None:
            if tz is None:
                raise ValueError('Please supply a target timezone')
            date_obj = date_obj.astimezone(tz)

        return date_obj.strftime(fmt)


def urljoin(*parts):
    """
    Join terms together with forward slashes

    Parameters
    ----------
    parts

    Returns
    -------
    str
    """
    # first strip extra forward slashes (except http:// and the likes) and
    # create list
    part_list = []
    for part in parts:
        p = str(part)
        if p.endswith('//'):
            p = p[0:-1]
        else:
            p = p.strip('/')
        part_list.append(p)
    # join everything together
    url = '/'.join(part_list)
    return url


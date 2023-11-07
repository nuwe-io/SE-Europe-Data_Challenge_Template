import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timedelta

def xml_to_gen_data(xml_data) -> dict:
    """
    Parse the XML data of generation into a dictionary of DataFrames, one for each PsrType.
    """

    # Define the XML namespace
    namespace = {'ns': 'urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'}
    
    # Parse the XML data
    root = ET.fromstring(xml_data)
    
    # Get all TimeSeries tags
    time_series_tags = root.findall('.//ns:TimeSeries', namespace)
    
    # Initialize a dictionary to hold the data
    data = {"StartTime": [], "EndTime": [], "AreaID": [], "UnitName": [], "PsrType": [], "quantity": []}

    # Loop over all TimeSeries tags
    for ts in time_series_tags:
        # Extract PsrType from MktPSRType if it exists
        psr_type_tag = ts.find('ns:MktPSRType/ns:psrType', namespace)
        psr_type = psr_type_tag.text if psr_type_tag is not None else None

        # Extract AreaID and UnitName if they exist
        area_id_tag = ts.find('ns:inBiddingZone_Domain.mRID', namespace)
        area_id = area_id_tag.text if area_id_tag is not None else None
        unit_name_tag = ts.find('ns:quantity_Measure_Unit.name', namespace)
        unit_name = unit_name_tag.text if unit_name_tag is not None else None

        # Extract the time period start and end if it exists
        time_period = ts.find('ns:Period', namespace)
        if time_period is not None:
            period_start = time_period.find('ns:timeInterval/ns:start', namespace).text
            period_end = time_period.find('ns:timeInterval/ns:end', namespace).text
            resolution = time_period.find('ns:resolution', namespace).text

            # Resolution is PT15M or PT60M
            resolution_minutes = int(resolution.replace('PT', '').replace('M', ''))

            # Extract the point values
            points = time_period.findall('ns:Point', namespace)
            for point in points:
                position = point.find('ns:position', namespace).text
                quantity = point.find('ns:quantity', namespace).text

                # Calculate the actual start and end time for each resolution_minutes interval
                start_time_interval = datetime.fromisoformat(period_start.replace('Z', '+00:00'))
                end_time_interval = start_time_interval + timedelta(minutes=resolution_minutes*(int(position)-1))
                start_time_interval = end_time_interval - timedelta(minutes=resolution_minutes)

                # Append the StartTime, EndTime, AreaID, UnitName, PsrType, and quantity values to the data dictionary
                data["StartTime"].append(start_time_interval.isoformat(timespec='minutes')+'Z')
                data["EndTime"].append(end_time_interval.isoformat(timespec='minutes')+'Z')
                data["AreaID"].append(area_id)
                data["UnitName"].append(unit_name)
                data["PsrType"].append(psr_type)
                data["quantity"].append(quantity)

    # Convert the data dictionary into a pandas DataFrame
    df = pd.DataFrame(data)

    # Create a separate DataFrame for each PsrType
    df_dict = {psr_type: df[df["PsrType"] == psr_type] for psr_type in df["PsrType"].unique()}
    
    return df_dict

def xml_to_load_dataframe(xml_data) -> pd.DataFrame:
    """
    Parse the XML data of Load into a pandas DataFrame.
    """
    namespace = {'ns': 'urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'}
    root = ET.fromstring(xml_data)

    data = []
    for time_series in root.findall('.//ns:TimeSeries', namespace):
        series_id = time_series.find('ns:mRID', namespace).text
        business_type = time_series.find('ns:businessType', namespace).text
        object_aggregation = time_series.find('ns:objectAggregation', namespace).text
        domain_mrid = time_series.find('ns:outBiddingZone_Domain.mRID', namespace).text
        unit_name = time_series.find('ns:quantity_Measure_Unit.name', namespace).text
        curve_type = time_series.find('ns:curveType', namespace).text

        for period in time_series.findall('ns:Period', namespace):
            start_time = period.find('ns:timeInterval/ns:start', namespace).text
            end_time = period.find('ns:timeInterval/ns:end', namespace).text
            resolution = period.find('ns:resolution', namespace).text

            # Resolution is PT15M or PT60M
            resolution_minutes = int(resolution.replace('PT', '').replace('M', ''))
            
            for point in period.findall('ns:Point', namespace):
                position = point.find('ns:position', namespace).text
                quantity = point.find('ns:quantity', namespace).text

                # calculate the actual start and end time for each resolution_minutes interval
                start_time_interval = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_time_interval = start_time_interval + timedelta(minutes=resolution_minutes*(int(position)-1))
                start_time_interval = end_time_interval - timedelta(minutes=resolution_minutes)

                data.append([start_time_interval.isoformat(timespec='minutes')+'Z', end_time_interval.isoformat(timespec='minutes')+'Z', 
                             domain_mrid, unit_name, quantity])

    df = pd.DataFrame(data, columns=['StartTime', 'EndTime', 'AreaID', 'UnitName', 'Load'])
    return df

def make_url(base_url, params):
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"

def perform_get_request(base_url, params):
    url = make_url(base_url, params)
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return response.content
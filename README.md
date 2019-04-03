# Sentinel-1 Single Look Complex (SLC) data on AWS

According to the data usage policy of ESA, Sentinel-1 (S1) Single Look Complex (SLC) data is free and open to the public. Under the same policy, S1 SLC data for Interferometric Wide (IW) beam mode is hosted on AWS S3 storage as an open dataset. The data are available since the launch of the S1 satellite and will be continuously updated as the data are made available on ESA and subsequently on the AWS S3 bucket. 
The S1 SLC dataset contains Synthetic Aperture Radar (SAR) data obtained by the sensor Sentinel-1 operating in the microwave C-Band wavelength. The SAR sensors are installed on a two-satellite (Sentinel-1A and Sentinel-1B) constellation orbiting the Earth, operated by the European Space Agency. The S1 SLC data are a Level-1 product that consists of focused SAR data in zero-Doppler slant-range geometry, suitable for advanced processing with fewer processing steps as compared to Level-0 raw products. The Level-1 SLC product also preserves the radar backscatter amplitude and phase information in all-weather, day or night conditions, which is ideal for studying natural hazards and emergency response, land applications, oil spill monitoring, sea-ice conditions, and associated climate-change effects.


## Accessing S1 SLC on AWS (South and Southeast Asia, Taiwan, and Japan)

We ingest Sentinel-1A/B Level-1 Interferometric Wideswath(IW) SLC over the following region of interest:
<p align="center">
<img src="https://github.com/earthobservatory/sentinel1-opds/blob/master/misc/opendatasetaoi.png" width="650">
</p>

Specific geojson coordinates of the region of interest can be found [here](https://github.com/earthobservatory/sentinel1-opds/blob/master/scripts/opendataset.geojson).

### AWS S3 bucket link structure

S1 SLC IW mode data is organized using a directory structure that is based on the **start date of the acquisition**. Please refer to Table 1 for the description of different elements of the S3 bucket link.

---

_s3://sentinel1-slc-seasia-pds/datasets/slc/v1.1/_
**`YYYY`/`MM`/`DD`/`XXX`\_`BB`\_SLC\_\_1S`PP`\_`YYYYMMDD`T`HHMMSS`\_`yyyymmdd`T`hhmmss`\_`OOOOOO`\_`DDDDDD`\_`CCCC`**

---


|Variable      |Description                |Details (code: code details)|
|--------------|---------------------------|----------------------------|
|**`XXX`**      |Denotes the satellite       |S1A: Sentinel-1A <br>S1B: Sentinel-1B|
|**`BB`**       |Acquisition Mode            |IW: Interferometric Wide-Swath       |
|**`PP`**       |Polarisation                |SH:single HH polarisation <br>SV:	single VV polarisation<br>DH:	dual HH+HV polarisation <br>DV:	dual VV+VH polarisation <br>HH:	Partial Dual polarisation, HH only <br>HV:	Partial Dual polarisation, HV only <br>VV:	Partial Dual polarisation, VV only <br>VH:	Partial Dual polarisation, VV only|
|**`YYYYMMDD`** |Acquisition Start Date (UTC)|Four-digit year, two-digit month, two-digit day|
|**`HHMMSS`**   |Acquisition Start Time (UTC)|Two-digit hour, two-digit minutes, two-digit seconds|
|**`yyyymmdd`** |Acquisition End Date (UTC)  |Four-digit year, two-digit month, two-digit day|
|**`hhmmss`**   |Acquisition End Time (UTC)  |Two-digit hour, two-digit minutes, two-digit seconds|
|**`OOOOOO`**   |Absolute orbit number at product start time |In the range of 000001-999999|
|**`DDDDDD`**   |Mission data take ID        |In the range 000001-FFFFFF|
|**`CCC`**      |Hexadecimal string generated from CRC-16 of the manifest file |CRC-16 algorithm used to compute the unique identifier is CRC-CCITT (0xFFFF)|

Table 1: Description of elements included in AWS S3 bucket link 
([_Source_](https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-1-sar/products-algorithms/level-1-product-formatting))
 
For instance, a scene directory will look like the following: 

```
s3://sentinel1-slc-seasia-pds/datasets/slc/v1.1/2018/02/09/S1B_IW_SLC__1SDV_20180209T100011_20180209T100047_009545_0112FD_00E6
``` 

**or**

```
http://sentinel1-slc-seasia-pds.s3-website-ap-southeast-1.amazonaws.com/datasets/slc/v1.1/2018/02/09/S1B_IW_SLC__1SDV_20180209T100011_20180209T100047_009545_0112FD_00E6
```

Where S1B is Sentinel-1B (S1B), IW is Interferometric Wide-swath, DV is dual VV+VH polarization of the SLC data, acquired start date-time on 9th Feb 2018 (2018/02/09) at 10:00:11, acquired end date-time on 9th Feb 2018 (2018/02/09) at 10:00:47, orbit number 009545, mission data-take ID of 0112FD, and product unique identifier of 00E6 (refer to Table 1).

### Catalog

A csv describing all available scenes is available at:

```
s3://sentinel1-slc-seasia-pds/datasets/slc/v1.1/catalog.csv
```

**or**

```
http://sentinel1-slc-seasia-pds.s3-website-ap-southeast-1.amazonaws.com/datasets/slc/v1.1/catalog.csv
```
This list will be updated daily at 16:00:00 UTC.


### Product Directory

Each S1 SLC scene’s directory includes:
 - A compressed (.zip) Sentinel-1 SAR product folder in the [SAFE](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/data-formats/safe-specification) format, which comprises of the following:
     - a 'manifest.safe' file which holds the general product information in XML
     - a measurement folder with complex measurement data set in GeoTIFF format per sub-swath per polarisation
     - a preview folder containing 'quicklooks' in PNG format, Google Earth overlays in KML format and HTML preview files
     - an annotation folder containing the product metadata in XML as well as calibration data
     - a support folder containing the XML schemes describing the product XML.
     
 - A large quicklook preview png (browse.png) of the swath
 - A small quicklook preview png (browse_small.png) of the swath with longest dimension at 250px
 - Metadata file (met.json) specifying SLC acquisition parameters such as: 
     - orbit direction
     - orbit cycle
     - track number
     - polygon of acquired area.
 - Other metadata files (context.json, datasets.json) created by the ingestion system to track ingest jobs.


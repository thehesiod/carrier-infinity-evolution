from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Dict

import dateutil.parser


def ensure_database(path: Path):
    if not path:
        return

    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute('''\
        create table if not exists energy_usage
        (
            id integer primary key,
            
            ts real not null,
            
            -- day, year, month
            period_type text not null, 
            period_year integer not null,
            period_month integer not null,
            period_day integer not null,
            
            cooling real not null,
            hpheat real not null,
            fan real not null,
            eheat real not null,
            reheat real not null,
            fangas real not null,
            gas real not null,
            looppump real not null
        )''')

    c.execute('''\
        -- this is a pointer the the latest version of a given period
        create table if not exists energy_period_usage
        (            
            -- day, year, month
            period_type text not null, 
            period_year integer not null,
            period_month integer not null,
            period_day integer not null,
            
            eu_id integer not null,
            primary key(period_type, period_year, period_month, period_day)
            foreign key (eu_id) references energy_usage(id)
        )''')

    c.execute('''\
        create table if not exists odu_status
        (
            ts timestamp not null,
            odutype text not null,
            opstat integer not null,
            opmode text not null,
            iducfm integer not null,
            lat integer not null,
            oat integer not null,
            oducoiltmp integer not null,
            blwrpm integer not null,
            linevolt integer not null,
            lockactive text not null,
            locktime integer not null,
            comprpm integer not null,
            suctpress integer not null,
            sucttemp integer not null,
            suctsupheat real not null,
            dischargetmp integer not null,
            sparesensorstatus text not null,
            sparesensorvalue integer not null,
            exvpos integer not null,
            curtail stext not null,
            statpress real not null,
            enterreftmp integer not null,
            availminheatstage integer not null,
            availmaxheatstage integer not null,
            availmincoolstage integer not null,
            availmaxcoolstage integer not null,
            opminheatstage integer not null,
            opmaxheatstage integer not null,
            opmincoolstage integer not null,
            opmaxcoolstage integer not null,
            aclinecurrent real,
            dcbusvoltage real,
            dischargepressure real,
            dischargesuperheat real,
            exvposvi_unit text not null,
            exvposvi_value integer not null,
            ipmtemperature real,
            lowambientcooling text not null,
            pfcmtemperature real,
            outdoorfanrpm real
        )''')

    conn.commit()


def write_energy_data(path: Path, data: Dict):
    if not path:
        return

    # day1 = yesterday, day2 = two days ago
    conn = sqlite3.connect(path)
    c = conn.cursor()

    ts = dateutil.parser.isoparse(data['timestamp'])
    data = [

    ]
    c.execute('''\
        insert into energy_usage(
            timestamp, period_type, period_year, period_month, period_day, cooling, hpheat, fan, eheat, reheat, fangas, gas, looppump
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()


def write_odu_status(path: Path, data: Dict):
    if not path:
        return

    # day1 = yesterday, day2 = two days ago
    conn = sqlite3.connect(path)
    c = conn.cursor()

    ts = dateutil.parser.isoparse(data['timestamp'])
    params = [
        ts,
        data['odutype'],
        data['opstat'],
        data['opmode'],
        data['iducfm'],
        data['lat'],
        data['oat'],
        data['oducoiltmp'],
        data['blwrpm'],
        data['linevolt'],
        data['lockactive'],
        data['locktime'],
        data['comprpm'],
        data['suctpress'],
        data['sucttemp'],
        data['suctsupheat'],
        data['dischargetmp'],
        data['sparesensorstatus'],
        data['sparesensorvalue'],
        data['exvpos'],
        data['curtail'],
        data['statpress'],
        data['enterreftmp'],
        data['availminheatstage'],
        data['availmaxheatstage'],
        data['availmincoolstage'],
        data['availmaxcoolstage'],
        data['opminheatstage'],
        data['opmaxheatstage'],
        data['opmincoolstage'],
        data['opmaxcoolstage'],
        data['aclinecurrent'],
        data['dcbusvoltage'],
        data['dischargepressure'],
        data['dischargesuperheat'],
        data['exvposvi']['$']['unit'],
        data['exvposvi']['_'],
        data['ipmtemperature'],
        data['lowambientcooling'],
        data['pfcmtemperature'],
        data['outdoorfanrpm']
    ]
    try:
        c.execute(f'''\
            insert into odu_status(
                ts, odutype, opstat, opmode, iducfm, lat, oat, oducoiltmp, blwrpm, linevolt, lockactive, locktime, comprpm, suctpress, sucttemp, suctsupheat, dischargetmp, sparesensorstatus, sparesensorvalue,
                exvpos, curtail, statpress, enterreftmp, availminheatstage, availmaxheatstage,availmincoolstage, availmaxcoolstage, opminheatstage, opmaxheatstage, opmincoolstage, opmaxcoolstage, 
                aclinecurrent, dcbusvoltage, dischargepressure, dischargesuperheat, exvposvi_unit, exvposvi_value, ipmtemperature, lowambientcooling, pfcmtemperature, outdoorfanrpm
            ) values ({','.join(['?' for _ in range(len(params))])})''', params)
        conn.commit()
    except:
        print(f'Unable to push params: {params}')
        raise
    finally:
        conn.close()

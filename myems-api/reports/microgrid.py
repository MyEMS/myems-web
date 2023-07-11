from datetime import datetime, timedelta, timezone
from decimal import Decimal
import falcon
import mysql.connector
import simplejson as json
from core.useractivity import access_control, api_key_control
import config


class Reporting:
    @staticmethod
    def __init__():
        """Initializes Class"""
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    ####################################################################################################################
    # PROCEDURES
    # Step 1: valid parameters
    # Step 2: query the microgrid
    # Step 3: query associated batteries
    # Step 4: query associated converters
    # Step 5: query associated evchargers
    # Step 6: query associated generators
    # Step 7: query associated grids
    # Step 8: query associated heatpumps
    # Step 9: query associated inverters
    # Step 10: query associated loads
    # Step 11: query associated photovoltaics
    # Step 12: query associated sensors
    # Step 13: query associated windturbines
    # Step 14: query associated meters data
    # Step 15: query associated points data
    # Step 16: construct the report
    ####################################################################################################################
    @staticmethod
    def on_get(req, resp):
        if 'API-KEY' not in req.headers or \
                not isinstance(req.headers['API-KEY'], str) or \
                len(str.strip(req.headers['API-KEY'])) == 0:
            access_control(req)
        else:
            api_key_control(req)
        print(req.params)
        microgrid_id = req.params.get('microgridid')

        ################################################################################################################
        # Step 1: valid parameters
        ################################################################################################################
        if microgrid_id is None:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ID')
        else:
            microgrid_id = str.strip(microgrid_id)
            if not microgrid_id.isdigit() or int(microgrid_id) <= 0:
                raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_MICROGRID_ID')

        reporting_start_datetime_utc = datetime.utcnow() - timedelta(days=1)
        reporting_end_datetime_utc = datetime.utcnow()

        ################################################################################################################
        # Step 2: Step 2: query the microgrid
        ################################################################################################################
        if not microgrid_id.isdigit() or int(microgrid_id) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ID')

        cnx_system = mysql.connector.connect(**config.myems_system_db)
        cursor_system = cnx_system.cursor()

        query = (" SELECT id, name, uuid "
                 " FROM tbl_microgrid_architecture_types ")
        cursor_system.execute(query)
        rows_architecture_types = cursor_system.fetchall()

        architecture_type_dict = dict()
        if rows_architecture_types is not None and len(rows_architecture_types) > 0:
            for row in rows_architecture_types:
                architecture_type_dict[row[0]] = {"id": row[0], "name": row[1], "uuid": row[2]}

        query = (" SELECT id, name, uuid "
                 " FROM tbl_microgrid_owner_types ")
        cursor_system.execute(query)
        rows_microgrid_owner_types = cursor_system.fetchall()

        microgrid_owner_type_dict = dict()
        if rows_microgrid_owner_types is not None and len(rows_microgrid_owner_types) > 0:
            for row in rows_microgrid_owner_types:
                microgrid_owner_type_dict[row[0]] = {"id": row[0],
                                                     "name": row[1],
                                                     "uuid": row[2]}

        query = (" SELECT id, name, uuid "
                 " FROM tbl_contacts ")
        cursor_system.execute(query)
        rows_contacts = cursor_system.fetchall()

        contact_dict = dict()
        if rows_contacts is not None and len(rows_contacts) > 0:
            for row in rows_contacts:
                contact_dict[row[0]] = {"id": row[0],
                                        "name": row[1],
                                        "uuid": row[2]}

        query = (" SELECT id, name, uuid "
                 " FROM tbl_cost_centers ")
        cursor_system.execute(query)
        rows_cost_centers = cursor_system.fetchall()

        cost_center_dict = dict()
        if rows_cost_centers is not None and len(rows_cost_centers) > 0:
            for row in rows_cost_centers:
                cost_center_dict[row[0]] = {"id": row[0],
                                            "name": row[1],
                                            "uuid": row[2]}

        query = (" SELECT id, name, uuid, "
                 "        address, postal_code, latitude, longitude, capacity, "
                 "        architecture_type_id, owner_type_id, "
                 "        contact_id, cost_center_id, description "
                 " FROM tbl_microgrids "
                 " WHERE id = %s ")
        cursor_system.execute(query, (microgrid_id,))
        row = cursor_system.fetchone()

        if row is None:
            cursor_system.close()
            cnx_system.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.MICROGRID_NOT_FOUND')
        else:
            architecture_type = architecture_type_dict.get(row[8], None)
            owner_type = microgrid_owner_type_dict.get(row[9], None)
            contact = contact_dict.get(row[10], None)
            cost_center = cost_center_dict.get(row[11], None)
            meta_result = {"id": row[0],
                           "name": row[1],
                           "uuid": row[2],
                           "address": row[3],
                           "postal_code": row[4],
                           "latitude": row[5],
                           "longitude": row[6],
                           "capacity": row[7],
                           "architecture_type": architecture_type,
                           "owner_type": owner_type,
                           "contact": contact,
                           "cost_center": cost_center,
                           "description": row[12],
                           "qrcode": 'microgrid:' + row[2]}

        point_list = list()
        meter_list = list()
        energy_category_set = set()

        # query all energy categories in system
        cursor_system.execute(" SELECT id, name, unit_of_measure, kgce, kgco2e "
                              " FROM tbl_energy_categories "
                              " ORDER BY id ", )
        rows_energy_categories = cursor_system.fetchall()
        if rows_energy_categories is None or len(rows_energy_categories) == 0:
            if cursor_system:
                cursor_system.close()
            if cnx_system:
                cnx_system.close()
            raise falcon.HTTPError(status=falcon.HTTP_404,
                                   title='API.NOT_FOUND',
                                   description='API.ENERGY_CATEGORY_NOT_FOUND')
        energy_category_dict = dict()
        for row_energy_category in rows_energy_categories:
            energy_category_dict[row_energy_category[0]] = {"name": row_energy_category[1],
                                                            "unit_of_measure": row_energy_category[2],
                                                            "kgce": row_energy_category[3],
                                                            "kgco2e": row_energy_category[4]}

        ################################################################################################################
        # Step 3: query associated batteries
        ################################################################################################################
        cursor_system.execute(" SELECT p.id, mb.name, p.units, p.object_type  "
                              " FROM tbl_microgrids_batteries mb, tbl_points p "
                              " WHERE mb.id = %s AND mb.power_point_id = p.id ",
                              (microgrid_id,))
        row_point = cursor_system.fetchone()
        if row_point is not None:
            point_list.append({"id": row_point[0],
                               "name": row_point[1]+'.P',
                               "units": row_point[2],
                               "object_type": row_point[3]})

        cursor_system.execute(" SELECT m.id, mb.name, m.energy_category_id  "
                              " FROM tbl_microgrids_batteries mb, tbl_meters m "
                              " WHERE mb.id = %s AND mb.charge_meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1] + '.Charge',
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])

        cursor_system.execute(" SELECT m.id, mb.name, m.energy_category_id  "
                              " FROM tbl_microgrids_batteries mb, tbl_meters m "
                              " WHERE mb.id = %s AND mb.discharge_meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1] + '.Discharge',
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])

        ################################################################################################################
        # Step 4: query associated converters
        ################################################################################################################

        ################################################################################################################
        # Step 5: query associated evchargers
        ################################################################################################################
        cursor_system.execute(" SELECT p.id, me.name, p.units, p.object_type  "
                              " FROM tbl_microgrids_evchargers me, tbl_points p "
                              " WHERE me.id = %s AND me.power_point_id = p.id ",
                              (microgrid_id,))
        row_point = cursor_system.fetchone()
        if row_point is not None:
            point_list.append({"id": row_point[0],
                               "name": row_point[1]+'.P',
                               "units": row_point[2],
                               "object_type": row_point[3]})

        cursor_system.execute(" SELECT m.id, me.name, m.energy_category_id  "
                              " FROM tbl_microgrids_evchargers me, tbl_meters m "
                              " WHERE me.id = %s AND me.meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1],
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])
        ################################################################################################################
        # Step 6: query associated generators
        ################################################################################################################
        cursor_system.execute(" SELECT p.id, mg.name, p.units, p.object_type  "
                              " FROM tbl_microgrids_generators mg, tbl_points p "
                              " WHERE mg.id = %s AND mg.power_point_id = p.id ",
                              (microgrid_id,))
        row_point = cursor_system.fetchone()
        if row_point is not None:
            point_list.append({"id": row_point[0],
                               "name": row_point[1]+'.P',
                               "units": row_point[2],
                               "object_type": row_point[3]})

        cursor_system.execute(" SELECT m.id, mg.name, m.energy_category_id  "
                              " FROM tbl_microgrids_generators mg, tbl_meters m "
                              " WHERE mg.id = %s AND mg.meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1],
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])
        ################################################################################################################
        # Step 7: query associated grids
        ################################################################################################################
        cursor_system.execute(" SELECT p.id, mg.name, p.units, p.object_type  "
                              " FROM tbl_microgrids_grids mg, tbl_points p "
                              " WHERE mg.id = %s AND mg.power_point_id = p.id ",
                              (microgrid_id,))
        row_point = cursor_system.fetchone()
        if row_point is not None:
            point_list.append({"id": row_point[0],
                               "name": row_point[1]+'.P',
                               "units": row_point[2],
                               "object_type": row_point[3]})

        cursor_system.execute(" SELECT m.id, mg.name, m.energy_category_id  "
                              " FROM tbl_microgrids_grids mg, tbl_meters m "
                              " WHERE mg.id = %s AND mg.buy_meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1],
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])

        cursor_system.execute(" SELECT m.id, mg.name, m.energy_category_id  "
                              " FROM tbl_microgrids_grids mg, tbl_meters m "
                              " WHERE mg.id = %s AND mg.sell_meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1],
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])

        ################################################################################################################
        # Step 8: query associated heatpumps
        ################################################################################################################
        cursor_system.execute(" SELECT p.id, mh.name, p.units, p.object_type  "
                              " FROM tbl_microgrids_heatpumps mh, tbl_points p "
                              " WHERE mh.id = %s AND mh.power_point_id = p.id ",
                              (microgrid_id,))
        row_point = cursor_system.fetchone()
        if row_point is not None:
            point_list.append({"id": row_point[0],
                               "name": row_point[1]+'.P',
                               "units": row_point[2],
                               "object_type": row_point[3]})

        cursor_system.execute(" SELECT m.id, mh.name, m.energy_category_id  "
                              " FROM tbl_microgrids_heatpumps mh, tbl_meters m "
                              " WHERE mh.id = %s AND mh.electricity_meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1] + '.Electricity',
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])

        cursor_system.execute(" SELECT m.id, mh.name, m.energy_category_id  "
                              " FROM tbl_microgrids_heatpumps mh, tbl_meters m "
                              " WHERE mh.id = %s AND mh.heat_meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1] + '.Heat',
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])

        cursor_system.execute(" SELECT m.id, mh.name, m.energy_category_id  "
                              " FROM tbl_microgrids_heatpumps mh, tbl_meters m "
                              " WHERE mh.id = %s AND mh.cooling_meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1] + '.Cooling',
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])

        ################################################################################################################
        # Step 9: query associated inverters
        ################################################################################################################

        ################################################################################################################
        # Step 10: query associated loads
        ################################################################################################################
        cursor_system.execute(" SELECT p.id, ml.name, p.units, p.object_type  "
                              " FROM tbl_microgrids_loads ml, tbl_points p "
                              " WHERE ml.id = %s AND ml.power_point_id = p.id ",
                              (microgrid_id,))
        row_point = cursor_system.fetchone()
        if row_point is not None:
            point_list.append({"id": row_point[0],
                               "name": row_point[1]+'.P',
                               "units": row_point[2],
                               "object_type": row_point[3]})

        cursor_system.execute(" SELECT m.id, ml.name, m.energy_category_id  "
                              " FROM tbl_microgrids_loads ml, tbl_meters m "
                              " WHERE ml.id = %s AND ml.meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1],
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])
        ################################################################################################################
        # Step 11: query associated photovoltaics
        ################################################################################################################
        cursor_system.execute(" SELECT p.id, mp.name, p.units, p.object_type  "
                              " FROM tbl_microgrids_photovoltaics mp, tbl_points p "
                              " WHERE mp.id = %s AND mp.power_point_id = p.id ",
                              (microgrid_id,))
        row_point = cursor_system.fetchone()
        if row_point is not None:
            point_list.append({"id": row_point[0],
                               "name": row_point[1]+'.P',
                               "units": row_point[2],
                               "object_type": row_point[3]})

        cursor_system.execute(" SELECT m.id, mp.name, m.energy_category_id  "
                              " FROM tbl_microgrids_photovoltaics mp, tbl_meters m "
                              " WHERE mp.id = %s AND mp.meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1],
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])
        ################################################################################################################
        # Step 12: query associated sensors
        ################################################################################################################

        ################################################################################################################
        # Step 13: query associated windturbines
        ################################################################################################################
        cursor_system.execute(" SELECT p.id, mw.name, p.units, p.object_type  "
                              " FROM tbl_microgrids_windturbines mw, tbl_points p "
                              " WHERE mw.id = %s AND mw.power_point_id = p.id ",
                              (microgrid_id,))
        row_point = cursor_system.fetchone()
        if row_point is not None:
            point_list.append({"id": row_point[0],
                               "name": row_point[1]+'.P',
                               "units": row_point[2],
                               "object_type": row_point[3]})

        cursor_system.execute(" SELECT m.id, mw.name, m.energy_category_id  "
                              " FROM tbl_microgrids_windturbines mw, tbl_meters m "
                              " WHERE mw.id = %s AND mw.meter_id = m.id ",
                              (microgrid_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is not None:
            meter_list.append({"id": row_meter[0],
                               "name": row_meter[1],
                               "energy_category_id": row_meter[2]})
            energy_category_set.add(row_meter[2])
        ################################################################################################################
        # Step 14: query associated meters data
        ################################################################################################################
        timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
        if config.utc_offset[0] == '-':
            timezone_offset = -timezone_offset

        cnx_energy = mysql.connector.connect(**config.myems_energy_db)
        cursor_energy = cnx_energy.cursor()

        reporting = dict()
        meter_report_list = list()
        if energy_category_set is not None and len(energy_category_set) > 0:
            for energy_category_id in energy_category_set:
                for meter in meter_list:
                    if energy_category_id != meter['energy_category_id']:
                        continue
                    cursor_energy.execute(" SELECT start_datetime_utc, actual_value "
                                          " FROM tbl_meter_hourly "
                                          " WHERE meter_id = %s "
                                          "     AND start_datetime_utc >= %s "
                                          "     AND start_datetime_utc < %s "
                                          " ORDER BY start_datetime_utc ",
                                          (meter['id'],
                                           reporting_start_datetime_utc,
                                           reporting_end_datetime_utc))
                    rows_meter_hourly = cursor_energy.fetchall()
                    if rows_meter_hourly is not None and len(rows_meter_hourly) > 0:
                        meter_report = dict()
                        meter_report['timestamps'] = list()
                        meter_report['values'] = list()
                        meter_report['subtotal'] = Decimal(0.0)

                        for row_meter_hourly in rows_meter_hourly:
                            current_datetime_local = row_meter_hourly[0].replace(tzinfo=timezone.utc) + \
                                                     timedelta(minutes=timezone_offset)
                            current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')

                            actual_value = Decimal(0.0) if row_meter_hourly[1] is None else row_meter_hourly[1]

                            meter_report['timestamps'].append(current_datetime)
                            meter_report['values'].append(actual_value)
                            meter_report['subtotal'] += actual_value
                            meter_report['meter_name'] = meter['name']

                        meter_report_list.append(meter_report)

        ################################################################################################################
        # Step 15: query associated points data
        ################################################################################################################
        cnx_historical = mysql.connector.connect(**config.myems_historical_db)
        cursor_historical = cnx_historical.cursor()

        parameters_data = dict()
        parameters_data['names'] = list()
        parameters_data['timestamps'] = list()
        parameters_data['values'] = list()

        for point in point_list:
            point_values = []
            point_timestamps = []
            if point['object_type'] == 'ENERGY_VALUE':
                query = (" SELECT utc_date_time, actual_value "
                         " FROM tbl_energy_value "
                         " WHERE point_id = %s "
                         "       AND utc_date_time BETWEEN %s AND %s "
                         " ORDER BY utc_date_time ")
                cursor_historical.execute(query, (point['id'],
                                                  reporting_start_datetime_utc,
                                                  reporting_end_datetime_utc))
                rows = cursor_historical.fetchall()

                if rows is not None and len(rows) > 0:
                    for row in rows:
                        current_datetime_local = row[0].replace(tzinfo=timezone.utc) + \
                                                 timedelta(minutes=timezone_offset)
                        current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
                        point_timestamps.append(current_datetime)
                        point_values.append(row[1])
            elif point['object_type'] == 'ANALOG_VALUE':
                query = (" SELECT utc_date_time, actual_value "
                         " FROM tbl_analog_value "
                         " WHERE point_id = %s "
                         "       AND utc_date_time BETWEEN %s AND %s "
                         " ORDER BY utc_date_time ")
                cursor_historical.execute(query, (point['id'],
                                                  reporting_start_datetime_utc,
                                                  reporting_end_datetime_utc))
                rows = cursor_historical.fetchall()

                if rows is not None and len(rows) > 0:
                    for row in rows:
                        current_datetime_local = row[0].replace(tzinfo=timezone.utc) + \
                                                 timedelta(minutes=timezone_offset)
                        current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
                        point_timestamps.append(current_datetime)
                        point_values.append(row[1])
            elif point['object_type'] == 'DIGITAL_VALUE':
                query = (" SELECT utc_date_time, actual_value "
                         " FROM tbl_digital_value "
                         " WHERE point_id = %s "
                         "       AND utc_date_time BETWEEN %s AND %s "
                         " ORDER BY utc_date_time ")
                cursor_historical.execute(query, (point['id'],
                                                  reporting_start_datetime_utc,
                                                  reporting_end_datetime_utc))
                rows = cursor_historical.fetchall()

                if rows is not None and len(rows) > 0:
                    for row in rows:
                        current_datetime_local = row[0].replace(tzinfo=timezone.utc) + \
                                                 timedelta(minutes=timezone_offset)
                        current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
                        point_timestamps.append(current_datetime)
                        point_values.append(row[1])

            parameters_data['names'].append(point['name'] + ' (' + point['units'] + ')')
            parameters_data['timestamps'].append(point_timestamps)
            parameters_data['values'].append(point_values)
        ################################################################################################################
        # Step 16: construct the report
        ################################################################################################################
        result = dict()
        result['microgrid'] = meta_result
        result['meters'] = None
        result['parameters'] = {
            "names": parameters_data['names'],
            "timestamps": parameters_data['timestamps'],
            "values": parameters_data['values']
        }
        result['reporting_period'] = dict()
        result['reporting_period']['names'] = list()
        result['reporting_period']['energy_category_ids'] = list()
        result['reporting_period']['units'] = list()
        result['reporting_period']['timestamps'] = list()
        result['reporting_period']['values'] = list()
        result['reporting_period']['subtotals'] = list()

        if energy_category_set is not None and len(energy_category_set) > 0:
            for energy_category_id in energy_category_set:
                result['reporting_period']['names'].append(energy_category_dict[energy_category_id]['name'])
                result['reporting_period']['energy_category_ids'].append(energy_category_id)
                result['reporting_period']['units'].append(energy_category_dict[energy_category_id]['unit_of_measure'])
                # result['reporting_period']['timestamps'].append(reporting[energy_category_id]['timestamps'])
                # result['reporting_period']['values'].append(reporting[energy_category_id]['values'])
                # result['reporting_period']['subtotals'].append(reporting[energy_category_id]['subtotal'])

        resp.text = json.dumps(result)

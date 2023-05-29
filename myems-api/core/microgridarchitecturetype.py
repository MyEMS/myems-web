import uuid

import falcon
import mysql.connector
import simplejson as json

import config
from core.useractivity import user_logger, access_control


class MicrogridArchitectureTypeCollection:
    @staticmethod
    def __init__():
        """ Initializes MicrogridArchitectureTypeCollection"""
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid, description, simplified_code "
                 " FROM tbl_microgrid_architecture_types "
                 " ORDER BY id ")
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                meta_result = {"id": row[0], "name": row[1], "uuid": row[2],
                               "description": row[3], "simplified_code": row[4]}
                result.append(meta_result)

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp):
        """Handles POST requests"""
        access_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        new_values = json.loads(raw_json)

        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ARCHITECTURE_TYPE_NAME')

        name = str.strip(new_values['data']['name'])

        if 'description' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['description'], str) or \
                len(str.strip(new_values['data']['description'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ARCHITECTURE_TYPE_DESCRIPTION')

        description = str.strip(new_values['data']['description'])

        if 'simplified_code' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['simplified_code'], str) or \
                len(str.strip(new_values['data']['simplified_code'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ARCHITECTURE_TYPE_SIMPLIFIED_CODE')

        simplified_code = str.strip(new_values['data']['simplified_code'])

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_microgrid_architecture_types "
                       " WHERE name = %s ", (name,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.MICROGRID_ARCHITECTURE_TYPE_NAME_IS_ALREADY_IN_USE')

        cursor.execute(" SELECT simplified_code "
                       " FROM tbl_microgrid_architecture_types "
                       " WHERE simplified_code = %s ", (simplified_code,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.MICROGRID_ARCHITECTURE_TYPE_SIMPLIFIED_CODE_IS_ALREADY_IN_USE')

        add_value = (" INSERT INTO tbl_microgrid_architecture_types "
                     "    (name, uuid, description, simplified_code) "
                     " VALUES (%s, %s, %s, %s) ")
        cursor.execute(add_value, (name,
                                   str(uuid.uuid4()),
                                   description,
                                   simplified_code))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/microgridarchitecturetypes/' + str(new_id)


class MicrogridArchitectureTypeItem:
    @staticmethod
    def __init__():
        """ Initializes MicrogridArchitectureTypeItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ARCHITECTURE_TYPE_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid, description, simplified_code "
                 " FROM tbl_microgrid_architecture_types "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.close()
        if row is None:
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.MICROGRID_ARCHITECTURE_TYPE_NOT_FOUND')

        result = {"id": row[0],
                  "name": row[1],
                  "uuid": row[2],
                  "description": row[3],
                  "simplified_code": row[4]}
        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_):
        """Handles DELETE requests"""
        access_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ARCHITECTURE_TYPE_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_microgrid_architecture_types "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.MICROGRID_ARCHITECTURE_TYPE_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_microgrids "
                       " WHERE architecture_type_id = %s ", (id_,))
        rows_microgrids = cursor.fetchall()
        if rows_microgrids is not None and len(rows_microgrids) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.MICROGRID_ARCHITECTURE_TYPE_USED_IN_MICROGRID')

        cursor.execute(" DELETE FROM tbl_microgrid_architecture_types WHERE id = %s ", (id_,))
        cnx.commit()

        cursor.close()
        cnx.close()
        resp.status = falcon.HTTP_204

    @staticmethod
    @user_logger
    def on_put(req, resp, id_):
        """Handles PUT requests"""
        access_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ARCHITECTURE_TYPE_ID')

        new_values = json.loads(raw_json)
        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ARCHITECTURE_TYPE_NAME')

        name = str.strip(new_values['data']['name'])

        if 'description' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['description'], str) or \
                len(str.strip(new_values['data']['description'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ARCHITECTURE_TYPE_DESCRIPTION')

        description = str.strip(new_values['data']['description'])

        if 'simplified_code' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['simplified_code'], str) or \
                len(str.strip(new_values['data']['simplified_code'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MICROGRID_ARCHITECTURE_TYPE_SIMPLIFIED_CODE')

        simplified_code = str.strip(new_values['data']['simplified_code'])

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_microgrid_architecture_types "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.MICROGRID_ARCHITECTURE_TYPE_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_microgrid_architecture_types "
                       " WHERE name = %s AND id != %s ", (name, id_))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.MICROGRID_ARCHITECTURE_TYPE_NAME_IS_ALREADY_IN_USE')

        cursor.execute(" SELECT simplified_code "
                       " FROM tbl_microgrid_architecture_types "
                       " WHERE simplified_code = %s  AND id != %s ", (simplified_code, id_))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.BAD_REQUEST',
                                   description='API.MICROGRID_ARCHITECTURE_TYPE_SIMPLIFIED_CODE_IS_ALREADY_IN_USE')

        update_row = (" UPDATE tbl_microgrid_architecture_types "
                      " SET name = %s, description = %s, simplified_code = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (name,
                                    description,
                                    simplified_code,
                                    id_,))
        cnx.commit()
        cursor.close()
        cnx.close()
        resp.status = falcon.HTTP_200


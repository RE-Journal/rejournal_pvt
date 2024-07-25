import mysql.connector
from mysql.connector import Error
import pandas as pd
import decimal

def decimal_to_float(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(v) for v in obj]
    else:
        return obj

def get_db_connection():
    return mysql.connector.connect(
        host='193.203.184.1',
        user='u661384233_dbuser',
        password='Rejournal@123',
        database='u661384233_rejournal'
    )

def get_security_deposit_data(quarters, submarkets):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                COALESCE(submarket, 'Unknown') AS SUBMARKET,
                AVG(security_deposit_months) AS SECURITY_DEPOSIT
            FROM leases
            WHERE security_deposit_months IS NOT NULL
                AND lease_start_year = 2024
                AND lease_start_qtr IN ({})
                AND submarket IN ({})
            GROUP BY submarket
            ORDER BY SECURITY_DEPOSIT DESC
            """.format(','.join(['%s'] * len(quarters)), ','.join(['%s'] * len(submarkets)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, quarters + submarkets)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            df = pd.DataFrame(result)
            df['SECURITY_DEPOSIT'] = df['SECURITY_DEPOSIT'].round(1)
            
            return df.to_dict('records')
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_tenant_origin_share_data(quarters, submarkets):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                tenant_origin_continent AS Tenant_Origin,
                SUM(leasable_area_sq_ft) / 1000000 AS Area_Leased_Mln_Sqft
            FROM leases
            WHERE lease_start_year = 2024
                AND lease_start_qtr IN ({})
                AND submarket IN ({})
                AND tenant_origin_continent IS NOT NULL AND tenant_origin_continent != ''
            GROUP BY tenant_origin_continent
            ORDER BY Area_Leased_Mln_Sqft DESC
            """.format(','.join(['%s'] * len(quarters)), ','.join(['%s'] * len(submarkets)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, quarters + submarkets)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            df = pd.DataFrame(result)
            total_area = df['Area_Leased_Mln_Sqft'].sum()
            df['Percentage'] = (df['Area_Leased_Mln_Sqft'] / total_area * 100).round(2)
            
            return df.to_dict('records')
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_area_tenant_sector_share_data(quarters, submarkets):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                tenant_sector AS Tenant_Sector,
                SUM(leasable_area_sq_ft) / 1000000 AS Area_Leased_Mln_Sqft
            FROM leases
            WHERE lease_start_year = 2024
                AND lease_start_qtr IN ({})
                AND submarket IN ({})
                AND tenant_sector IS NOT NULL AND tenant_sector != ''
            GROUP BY tenant_sector
            ORDER BY Area_Leased_Mln_Sqft DESC
            """.format(','.join(['%s'] * len(quarters)), ','.join(['%s'] * len(submarkets)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, quarters + submarkets)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            df = pd.DataFrame(result)
            total_area = df['Area_Leased_Mln_Sqft'].sum()
            df['Percentage'] = (df['Area_Leased_Mln_Sqft'] / total_area * 100).round(1)
            
            return df.to_dict('records')
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_area_leased_by_submarket(quarters):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                submarket AS Submarket,
                SUM(leasable_area_sq_ft) / 1000000 AS Area_Leased_Mln_Sqft
            FROM leases
            WHERE lease_start_year = 2024
                AND lease_start_qtr IN ({})
                AND submarket IS NOT NULL AND submarket != ''
            GROUP BY submarket
            ORDER BY Area_Leased_Mln_Sqft DESC
            """.format(','.join(['%s'] * len(quarters)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, quarters)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            df = pd.DataFrame(result)
            total_area = df['Area_Leased_Mln_Sqft'].sum()
            df['Percentage'] = (df['Area_Leased_Mln_Sqft'] / total_area * 100).round(1)
            
            return df.to_dict('records')
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_tenant_sector_share_data(submarkets):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT
                CONCAT('2024 ', lease_start_qtr) AS Quarter,
                tenant_sector AS Tenant_Sector,
                SUM(leasable_area_sq_ft) AS Total_Area,
                (SUM(leasable_area_sq_ft) / SUM(SUM(leasable_area_sq_ft)) OVER (PARTITION BY lease_start_qtr)) * 100 AS Percentage
            FROM leases
            WHERE lease_start_year = 2024
                AND lease_start_qtr IN (1, 2)
                AND submarket IN ({})
                AND tenant_sector IS NOT NULL AND tenant_sector != ''
            GROUP BY lease_start_qtr, tenant_sector
            ORDER BY lease_start_qtr, Percentage ASC
            """.format(','.join(['%s'] * len(submarkets)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, submarkets)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            df = pd.DataFrame(result)
            df['Order'] = df.groupby('Quarter').cumcount()
            return df.to_dict('records')
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_quarterly_leasing_trend(submarkets):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                CONCAT('2024 ', lease_start_qtr) AS Quarter,
                SUM(leasable_area_sq_ft) / 1000000 AS Area_Leased_in_mln_sft
            FROM leases
            WHERE lease_start_year = 2024
                AND lease_start_qtr IN (1, 2)
                AND submarket IN ({})
            GROUP BY lease_start_qtr
            ORDER BY lease_start_qtr
            """.format(','.join(['%s'] * len(submarkets)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, submarkets)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            return result
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_average_monthly_rental_trend(submarkets):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                CONCAT('2024 ', lease_start_qtr) AS Quarter,
                AVG(average_monthly_rent_on_leasable_inr_psf) AS Average_Rent
            FROM leases
            WHERE lease_start_year = 2024
                AND lease_start_qtr IN (1, 2)
                AND submarket IN ({})
                AND average_monthly_rent_on_leasable_inr_psf IS NOT NULL
            GROUP BY lease_start_qtr
            ORDER BY lease_start_qtr
            """.format(','.join(['%s'] * len(submarkets)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, submarkets)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            return result
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_lease_start_rent_by_submarket(quarters, submarkets):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                submarket AS SUBMARKET,
                CONCAT(lease_start_qtr,'-', lease_start_year) AS Quarter,
                AVG(lease_start_rent_on_leasable_inr_psf) AS Average_Rent
            FROM leases
            WHERE submarket IS NOT NULL 
                AND lease_start_rent_on_leasable_inr_psf IS NOT NULL
                AND lease_start_year = 2024
                AND lease_start_qtr IN ({})
                AND submarket IN ({})
            GROUP BY submarket, lease_start_year, lease_start_qtr
            ORDER BY submarket, lease_start_year, lease_start_qtr
            """.format(','.join(['%s'] * len(quarters)), ','.join(['%s'] * len(submarkets)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, quarters + submarkets)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            return result
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_area_leased_by_sector(quarters, submarkets):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                project_category AS Project_Category,
                SUM(leasable_area_sq_ft) / 1000000 AS Area_Leased_Mln_Sqft
            FROM leases
            WHERE lease_start_year = 2024
                AND lease_start_qtr IN ({})
                AND submarket IN ({})
                AND project_category IS NOT NULL AND project_category != ''
            GROUP BY project_category
            ORDER BY Area_Leased_Mln_Sqft DESC
            """.format(','.join(['%s'] * len(quarters)), ','.join(['%s'] * len(submarkets)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, quarters + submarkets)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            df = pd.DataFrame(result)
            total_area = df['Area_Leased_Mln_Sqft'].sum()
            df['Percentage'] = (df['Area_Leased_Mln_Sqft'] / total_area * 100).round(1)
            
            return df.to_dict('records')
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_area_sold_by_submarket(quarters):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT
                submarket,
                SUM(area_sold_sqft) as total_area_sold
            FROM sales
            WHERE submarket IS NOT NULL AND submarket != ''
                AND sale_year = 2024
                AND sale_qtr IN ({})
            GROUP BY submarket
            ORDER BY total_area_sold DESC
            """.format(','.join(['%s'] * len(quarters)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, quarters)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            df = pd.DataFrame(result)
            total_area = df['total_area_sold'].sum()
            df['percentage'] = (df['total_area_sold'] / total_area * 100).round(2)
            
            return df.to_dict('records')
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_area_sold_by_quarter(quarters):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT
                CONCAT('', sale_qtr) as QTR,
                SUM(area_sold_sqft) as total_area_sold
            FROM sales
            WHERE sale_year = 2024 AND sale_qtr IN ({})
            GROUP BY sale_qtr
            ORDER BY sale_qtr
            """.format(','.join(['%s'] * len(quarters)))
           
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, quarters)
                result = cursor.fetchall()
           
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            df = pd.DataFrame(result)
            
            # Calculate the percentage
            total_area = df['total_area_sold'].sum()
            df['percentage'] = (df['total_area_sold'] / total_area * 100).round(2)
            
            return df.to_dict('records')
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_sales_by_buyer_type(quarters):
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                buyer_type,
                SUM(area_sold_sqft) as total_area_sold,
                SUM(total_value_inr) as total_value
            FROM sales
            WHERE buyer_type IS NOT NULL AND buyer_type != ''
                AND sale_year = 2024
                AND sale_qtr IN ({})
            GROUP BY buyer_type
            """.format(','.join(['%s'] * len(quarters)))
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, quarters)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            return result
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_submarkets():
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT DISTINCT submarket
            FROM leases
            WHERE submarket IS NOT NULL AND submarket != ''
            ORDER BY submarket
            """
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
            
            if not result:
                print("No submarkets found.")
                return []
            
            return [row['submarket'] for row in result]
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_leased_area_expiry_data():
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                lease_expiry_year AS expiry_year,
                SUM(area_transcatedsq_ft) / 1000000 AS area_mln_sqft
            FROM leases
            WHERE lease_expiry_year IS NOT NULL
                AND lease_expiry_year BETWEEN YEAR(CURDATE()) AND 2039
            GROUP BY lease_expiry_year
            ORDER BY expiry_year
            """
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return []
            
            result = decimal_to_float(result)
            return result
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def get_submarket_data():
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                submarket as label,
                SUM(area_transcatedsq_ft) as total_area
            FROM leases
            WHERE lease_start_year = 2024 AND lease_start_qtr IN (1, 2)
            GROUP BY submarket
            """
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return None
            
            result = decimal_to_float(result)
            df = pd.DataFrame(result)
            df['percentage'] = (df['total_area'] / df['total_area'].sum() * 100).round(2)
            return df.to_dict('records')
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()

def get_tenant_origin_data():
    try:
        connection = get_db_connection()
        if connection.is_connected():
            query = """
            SELECT 
                tenant_origin_continent as label,
                SUM(area_transcatedsq_ft) as total_area
            FROM leases
            WHERE lease_start_year = 2024 AND lease_start_qtr IN (1, 2)
            GROUP BY tenant_origin_continent
            """
            
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
            
            if not result:
                print("No data returned from the query.")
                return None
            
            result = decimal_to_float(result)
            df = pd.DataFrame(result)
            df['percentage'] = (df['total_area'] / df['total_area'].sum() * 100).round(2)
            return df.to_dict('records')
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()

#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
from celery import Celery

def revenue_check(connection,cid,days):
	try:
		with connection.cursor() as cursor:
			sql= '''
				    SELECT DATE(object_version),
					operation_id as OpId, 
					username, operation_status as status, 
					comment
					FROM operations 
					WHERE name='Bulk Upload' and 
					client_id=%s AND 
					object_version >= DATE_SUB(CURDATE(),INTERVAL %s DAY) AND 
					(description LIKE '%%Revenu%%' OR 
					description LIKE '%%Upload de receita%%' or 
					description LIKE '%%Carga de ingresos%%' OR 
					description LIKE '%%Carga de las figuras de seguimiento%%' OR 
					description LIKE '%%Umsatzdaten%%' OR 
					description LIKE '%%収益アップロード%%' or 
					description LIKE '%%トラッカー収益アップロード%%' OR 
					description LIKE '%%收入上%%' or 
					description LIKE'%%传收入%%')
					ORDER BY operation_id DESC; 
			'''
			cursor.execute(sql,(cid,days))
			result = cursor.fetchall()
			return result
	finally:
	 	connection.close()

def mkwid_query_lookup(connection,cid,mkwid,days):
#	try:
	with connection.cursor() as cursor:
		sql= '''
				SELECT  CONCAT(DATE(receive_time),'') as DATE_CONV,
				SUM(IF(publisher_group_id >=1,1,0)) as ATTR_CLICKS,
				COUNT(1) as TOTAL_CLICKS 
				FROM {} WHERE query LIKE '%{}%' 
				AND receive_time>=DATE_SUB(CURDATE(),INTERVAL {} DAY)
				AND action_id=1 
				GROUP BY DATE(receive_time) DESC WITH ROLLUP ;
			'''.format('tracker_data_'+str(cid),mkwid,days)
		print sql
		cursor.execute(sql)
		result = cursor.fetchall()
		connection.close()
		return result
	#finally:
	# 	connection.close()

def revenue_load_global(connection):
	try:
		with connection.cursor() as cursor :
			sql= ''' 
					SELECT rev.date,SUM(rev.revenue) revenue,SUM(rev.conversions) conversions,
					rev.currency,rev.last_modified,ct.name conv_name,
					IF(ct.many_per_click,'MANY','ONE') as many_p_cl, 
					IF(ct.aggregate_to_conversions,'TOTAL','---') as attr_tot_conv  
					FROM revenue_load_50268 as rev JOIN marin.conversion_types as ct USING(conversion_type_id)  
					WHERE rev.publisher_group_id IS NOT NULL and date='2015-07-31'
					GROUP BY rev.conversion_type_id,rev.last_modified; 
				'''
			cursor.execute(sql)
			result = cursor.fetchall()
			connection.close()
			return result
	finally:
	 	connection.close()


def simple_test(connection,query,params):
	try:
		with connection.cursor() as cursor :
			fmt_quer=query.format(**params)
			cursor.execute(fmt_quer)
			result = cursor.fetchall()
			#connection.close()
			return result
	finally:
	 	connection.close()

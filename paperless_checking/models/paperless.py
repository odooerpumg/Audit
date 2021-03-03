from odoo import models, fields, api, _
from datetime import date,timedelta,datetime
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError,ValidationError
import odoo.addons.decimal_precision as dp
import time
from odoo.tools.translate import _
import calendar
from dateutil.relativedelta import relativedelta
from requests.auth import HTTPBasicAuth
import hashlib
import json
import requests
import locale


class paperlessCategory(models.Model):
	_name = 'paperless.category'
	
	name = fields.Char('Name',required=True)
	code = fields.Char('Code',required=True)

class paperlessType(models.Model):
	_name = 'paperless.type'
	
	name = fields.Char('Name',required=True)

class paperlessBu(models.Model):
	_name = 'paperless.bu'
	
	name = fields.Char('Name',required=True)

class paperlessPrint(models.Model):
	_name = 'paperless.print'

	date = fields.Date('Date', default=fields.Date.today)
	bu_id = fields.Many2one('paperless.bu',string='BU',required=True)
	type_id = fields.Many2one('paperless.type',string='Type')

class CheckingName(models.Model):
	_name = 'paperless.checking.name'

	name = fields.Char('Name',required=True)

class paperlessMajorMinor(models.Model):
	_name = 'paperless.major.minor'
	
	name_id = fields.Many2one('paperless.checking.name',string='Name')
	category_id = fields.Many2one('paperless.category',string='Category')
	major = fields.Boolean('Major',default=False)
	minor = fields.Boolean('Minor',default=False)

	@api.model
	def checking_id_value(self):
		checking_value = {
			'checking_ids':[(4, self.checking_ids.id)],
		}
		self.write(checking_value)

	# @api.model
	# def create(self, vals):
	# 	# print "------create------------"
	# 	category = vals['category_id']
	# 	if vals['name_id']:
	# 		name = vals['name_id']
	# 		print('................. category = ',category,' and name = ',name)
	# 	result = super(paperlessMajorMinor, self).create(vals)
		
	# 	check_ids = self.env['paperless.category'].search([('id','=',category)])
	# 	print('............................ Category ids in mn ',check_ids)
	# 	name_ids = self.env['paperless.checking.name'].search([('id','=',name)])
	# 	print('............................ name ids in mn ',name_ids)
	# 	if check_ids and name_ids:
	# 		value = {'category_id': category}
	# 		print('................. value = ',value)
	# 		name_ids.write(value)
	# 	return result

	# def write(self,vals):
	# 	category = vals['category_id']
	# 	name = vals['name_id']
	# 	check_ids = self.env['paperless.category'].search([('id','=',category)])
	# 	print('............................ Category ids in mn ',check_ids)
	# 	name_ids = self.env['paperless.checking.name'].search([('id','=',name)])
	# 	print('............................ name ids in mn ',name_ids)
	# 	if check_ids and name_ids:
	# 		value = {'category_id': category}
	# 		print('................. value = ',value)
	# 		name_ids.write(value)
	# 	else:
	# 		raise ValidationError ('Category not match!')
	# 	record = super(paperlessMajorMinor, self).write(vals)
	# 	return record



class paperlessChecking(models.Model):
	_name = 'paperless.checking'
	
	
	name = fields.Char(string="Name")
	date = fields.Date('Date', default=fields.Date.today)
	bu_id = fields.Many2one('paperless.bu',string='BU')
	type_id = fields.Many2one('paperless.type',string='Type')
	mn_ids = fields.One2many('mn.line','checking_id',string='Major IDS',store=True)
	attach_ids = fields.One2many('paperless.attach','paper_id',string='Attachment',store=True)
	res_person = fields.Char('Responsible Person')
	department_id = fields.Many2one('hr.department',string='Department')
	state = fields.Selection([('draft', 'Draft'),
							('confirm', 'Confirm'),
							('fill', 'Fill'),
							('approve', 'Audit Approve')], string='State',default='draft')

	import_fname = fields.Char(string='Filename')
	import_file = fields.Binary(string='File')
# 	score_id = fields.Many2one('audit.score',string="Score")
	chk_count = fields.Integer(string='Checking Count',compute='_compute_activites_count')
	doc_sys = fields.Float(string='Document & System Control')
	cash = fields.Float(string='Cash Control')
	acc_receive = fields.Float(string='Account Receivable Control')
	stock = fields.Float(string='Stock Control')
	follow_up = fields.Float(string='Follow up Situation')
	total_control = fields.Float(string='Total')

	
	@api.model
	def create(self, vals):
		res = super(paperlessChecking,self).create(vals)
		res.name = 'PC'+str(res.id)
		return res
	
	
	def button_checking_entries(self):
		return {
			'name': _('Checking'),
			'view_mode': 'tree,form',
			'res_model': 'hr.employee',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('checking_ids', 'in', self.ids)],
		}

	def _compute_activites_count(self):
		check_chk = self.env['hr.employee'].search([('checking_ids', 'in', self.ids)])
		if check_chk:
			for chck in check_chk:
				self.chk_count +=1
		else:
			self.chk_count = 0

	def confirm(self):
		return self.write({'state': 'confirm'})

	def fill(self):
		return self.write({'state': 'fill'})


	def approve(self):
		return self.write({'state': 'approve'})

	def draft(self):
		return self.write({'state': 'draft'})
	
	def calculate(self):
		dsc_coutnt = 0
		t1 = 0
		cc_count = 0
		t2 = 0
		arc_count = 0
		t3 = 0
		sc_count = 0
		t4 = 0
		fus_count = 0
		t5 = 0
		lines = self.env['mn.line'].search([('checking_id', '=', self.id)])
		for line in lines:
			if line.category_id.code=='DSC':
				t1 += line.score_id.mark
				dsc_coutnt+=1
				
			elif line.category_id.code=='CC':
				t2 += line.score_id.mark
				cc_count+=1
			
			elif line.category_id.code=='ARC':
				t3 += line.score_id.mark
				arc_count+=1
				
			
			elif line.category_id.code=='SC':
				t4 += line.score_id.mark
				sc_count+=1
			
			elif line.category_id.code=='FUS':
				t5 += line.score_id.mark	
				fus_count+=1
		
		if dsc_coutnt>0:		
			self.doc_sys = t1/dsc_coutnt
		if cc_count>0:
			self.cash = t2/cc_count
		if arc_count>0:
			self.acc_receive = t3/arc_count
		if sc_count>0:
			self.stock = t4/sc_count
		if fus_count>0:
			self.follow_up = t5/fus_count
		self.total_control = self.doc_sys+self.cash+self.acc_receive+self.stock+self.follow_up	
		
class paperlessMNLine(models.Model):
	_name = 'mn.line'

	mn_id = fields.Many2one('paperless.major.minor',string='Major Minors')
	name_id = fields.Many2one('paperless.checking.name',string='Name',required=True)
	category_id = fields.Many2one('paperless.category',string='Category',stored=True)
	checking_id = fields.Many2one('paperless.checking',string='Paperless Checking',stored=True)
	major = fields.Boolean('Major',default=False,stored=True)
	minor = fields.Boolean('Minor',default=False,stored=True)
	check = fields.Boolean('Check',default=False)
	audit_remark = fields.Text('Audit Suggestion')
	cor_action_id = fields.Many2one('corrective.action',string='Corrective Action')
	root_cause = fields.Text('Root Cause')
	score_id = fields.Many2one('audit.score',string="Score")
	remark = fields.Text('Remark')

	@api.onchange('name_id')
	def onchange_mn_id(self):
		mn_ids = self.env['paperless.major.minor'].search([('name_id','=',self.name_id.id)])
		if mn_ids:
			self.category_id = mn_ids.category_id
			self.major = mn_ids.major
			self.minor = mn_ids.minor
					
class CorrectiveAction(models.Model):
	_name = 'corrective.action'

	name = fields.Char('Name')
	action_day = fields.Float('Action Days')

class Attachment(models.Model):
	_name = 'paperless.attach'
	
	name = fields.Char('Name')
	paper_id = fields.Many2one('paperless.checking',string='Paperless Checking')
	import_fname = fields.Char(string='Filename')
	import_file = fields.Binary(string='File')

class AuditScore(models.Model):
	_name = 'audit.score'

	name = fields.Char('Name')
	mark = fields.Integer('Mark')

class AuditAllocation(models.Model):
	_name = 'audit.allocation'

	audit_ids = fields.Many2many('hr.employee',string='Audit Person')
	checking_id = fields.Many2one('paperless.checking',string='Checking')

	def choose_audit(self, context=None):
		tbl_audit_obj = self.env['hr.employee']
		if context is None:
		  context = {}
		# data = self.read(self.ids)[0]
		if not self.audit_ids:
			raise ValidationError(_('Error!\n You must select Auditor (s) to generate.'))
		mn = self.audit_ids
		stu_ids = tbl_audit_obj.browse(mn)
		for mns in self.audit_ids:
			session_value = {
				'checking_ids':[(4, self.checking_id.id)],
				'checking_id':self.checking_id.id,
			}
			mns.write(session_value)

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	checking_id = fields.Many2one('paperless.checking',string='Checking')
	checking_ids = fields.Many2many('paperless.checking',stirng='Checking(s)')
	is_auditor = fields.Boolean('Is Auditor?')
	emp_no = fields.Integer('Employee Number')

	@api.model
	def checking_id_value(self):
		checking_value = {
			'checking_ids':[(4, self.checking_ids.id)],
		}
		print ("..............active id..........",self.checking_ids.id)
		self.write(checking_value)
# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api

class project_template_task(models.Model):

	_inherit = "project.task.type"

	project_check = fields.Boolean(string="Project Check")

class project_template(models.Model):

	_name = "project.template"

class project_project(models.Model):

	_inherit="project.project"

	@api.model
	def default_get(self, flds):
		stage_type_obj = self.env['project.task.type']
		state_new_id = stage_type_obj.search([('name','=','New')])
		if state_new_id:
			state_new_id.write({'sequence':1,'project_check':True})
		else:
			state_new_id = stage_type_obj.create({'name':'New','sequence':1,'project_check':True})
		state_in_progress_id = stage_type_obj.search([('name','=','In Progress')])
		if state_in_progress_id:
			state_in_progress_id.write({'sequence':2,'project_check':True})
		else:
			progress_id = stage_type_obj.create({'name':'In Progress','sequence':2,'project_check':True})
		state_cancel_id = stage_type_obj.search([('name','=','Cancelled')])
		if state_cancel_id:
			state_cancel_id.write({'sequence':3,'project_check':True})
		else:
			cancel_id = stage_type_obj.create({'name':'Cancelled','sequence':3,'project_check':True})
		state_pending_id = stage_type_obj.search([('name','=','Pending')])
		if state_pending_id:
			state_pending_id.write({'sequence':4,'project_check':True})
		else:
			pending_id = stage_type_obj.create({'name':'Pending','sequence':4,'project_check':True})
		state_closed_id = stage_type_obj.search([('name','=','Closed')])
		if state_closed_id:
			state_closed_id.write({'sequence':5,'project_check':True})
		else:
			closed_id = stage_type_obj.create({'name':'Closed','sequence':4,'project_check':True})
		stage_list=[]
		result = super(project_project, self).default_get(flds)
		result['stage_id']=state_new_id.id
		result['use_tasks'] = True
		return result

	@api.multi
	def count_sequence(self):
		stage_type_obj = self.env['project.task.type']
		state_in_progress_id = stage_type_obj.search([('name','=','In Progress')])
		state_template_id = stage_type_obj.search([('name','=','Template')])
		state_new_id = stage_type_obj.search([('name','=','New')])
		if self.stage_id.id == int(state_new_id):
			self.sequence_state=1
		elif self.stage_id.id == int(state_in_progress_id):
			self.sequence_state=2
		else:
			self.sequence_state=3
		
	@api.multi
	def set_template(self):
		stage_type_obj = self.env['project.task.type']
		state_template_id = stage_type_obj.search([('name','=','Template')])
		state_new_id = stage_type_obj.search([('name','=','New')])
		if state_template_id:
			state_template_id.write({'sequence':1,'project_check':True})
			state_new_id.update({'sequence':2,'project_check':True})
			self.update({'stage_id':state_template_id.id,'sequence_state':3})
		else:
			template_id = stage_type_obj.create({'name':'Template','sequence':1,'project_check':True})
			template_id.write({'sequence':1,'project_check':True})
			state_new_id.write({'sequence':2,'project_check':True})
			self.write({'stage_id':template_id.id,'sequence_state':3})
		state_template_id.write({'project_check':False})
			
	@api.multi
	def new_project(self):
		stage_type_obj = self.env['project.task.type']
		state_template_id = stage_type_obj.search([('name','=','Template')])
		state_new_id = stage_type_obj.search([('name','=','New')])
		project_id = self.create({
								'name':self.name,
								'use_tasks':self.use_tasks,
								'label_tasks':self.label_tasks,
								'user_id':self.user_id.id,
								'privacy_visibility':self.privacy_visibility,
								'partner_id':self.partner_id.id
							})
		if state_template_id:
			project_id.write({'stage_id':state_new_id.id,'sequence_state':1})
		return project_id

	@api.multi
	def reset_project(self):
		stage_type_obj = self.env['project.task.type']
		state_new_id = stage_type_obj.search([('name','=','New')])
		if state_new_id:
			self.write({'stage_id':state_new_id.id,'sequence_state':1})
		return 

	@api.multi
	def set_progress(self):
		stage_type_obj = self.env['project.task.type']
		state_progress_id = stage_type_obj.search([('name','=','In Progress')])
		if state_progress_id:
			self.write({'stage_id':state_progress_id.id,'sequence_state':2})
		return 
			
	stage_id = fields.Many2one('project.task.type',string="state")
	sequence_state = fields.Integer(compute="count_sequence",string="State Check")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
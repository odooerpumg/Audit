# -*- coding: utf-8 -*-
# from odoo import http


# class AuditExtension(http.Controller):
#     @http.route('/audit_extension/audit_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/audit_extension/audit_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('audit_extension.listing', {
#             'root': '/audit_extension/audit_extension',
#             'objects': http.request.env['audit_extension.audit_extension'].search([]),
#         })

#     @http.route('/audit_extension/audit_extension/objects/<model("audit_extension.audit_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('audit_extension.object', {
#             'object': obj
#         })

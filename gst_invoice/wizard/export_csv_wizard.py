#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models
import csv
from cStringIO import StringIO
import base64
from datetime import datetime

def _unescape(text):
    from urllib import unquote_plus
    try:
        text = unquote_plus(text.encode('utf8'))
        return text
    except Exception, e:
        return text

class ExportCsvWizard(models.TransientModel):
    _name = "export.csv.wizard"

    @api.model
    def exportCsv(self, active_ids, invoice_type, gstToolName):
        attachment = False
        respData = self.getInvoiceData(active_ids, invoice_type)
        mainData = respData[0]
        jsonData = respData[1]
        if mainData:
            fp = StringIO()
            writer = csv.writer(fp, quoting=csv.QUOTE_NONE)
            if invoice_type == 'b2b':
                columns = self.getB2BColumn()
                writer.writerow(columns)
            elif invoice_type == 'b2cl':
                columns = self.getB2CLColumn()
                writer.writerow(columns)
            elif invoice_type == 'b2cs':
                columns = self.getB2CSColumn()
                writer.writerow(columns)
            elif invoice_type == 'export':
                columns = self.getExportColumn()
                writer.writerow(columns)
            elif invoice_type == 'hsn':
                columns = self.getHSNColumn()
                writer.writerow(columns)
            for lineData in mainData:
                writer.writerow([_unescape(name) for name in lineData])
            fp.seek(0)
            data = fp.read()
            fp.close()
            attachment = self.generateAttachment(data, invoice_type, gstToolName)
        return [attachment, jsonData]

    def generateAttachment(self, data, invoice_type, gstToolName):
        attachment = False
        base64Data = base64.encodestring(data)
        datas_fname = '{}_{}.csv'.format(invoice_type, gstToolName)
        try:
            resId = 0
            if self._context.get('gst_id'):
                resId = self._context.get('gst_id')
            attachment = self.env['ir.attachment'].create({
                'datas': base64Data,
                'type': 'binary',
                'res_model': 'gstr1.tool',
                'res_id': resId,
                'db_datas': datas_fname,
                'datas_fname': datas_fname,
                'name': datas_fname
                }
            )
        except ValueError:
            return attachment
        return attachment

    def getB2BColumn(self):
        columns = [
            'GSTIN/UIN of Recipient',
            'Invoice Number',
            'Invoice date',
            'Invoice Value',
            'Place Of Supply',
            'Reverse Charge',
            'Invoice Type',
            'E-Commerce GSTIN',
            'Rate',
            'Taxable Value',
            'Cess Amount'
        ]
        return columns

    def getB2CLColumn(self):
        columns = [
            'Invoice Number',
            'Invoice date',
            'Invoice Value',
            'Place Of Supply',
            'Rate',
            'Taxable Value',
            'Cess Amount',
            'E-Commerce GSTIN'
        ]
        return columns

    def getB2CSColumn(self):
        columns = [
            'Type',
            'Place Of Supply',
            'Rate',
            'Taxable Value',
            'Cess Amount',
            'E-Commerce GSTIN'
        ]
        return columns

    def getExportColumn(self):
        columns = [
            'Export Type',
            'Invoice Number',
            'Invoice date',
            'Invoice Value',
            'Port Code',
            'Shipping Bill Number',
            'Shipping Bill Date',
            'Rate',
            'Taxable Value'
        ]
        return columns

    def getHSNColumn(self):
        columns = [
            'HSN',
            'Description',
            'UQC',
            'Total Quantity',
            'Total Value',
            'Taxable Value',
            'Integrated Tax Amount',
            'Central Tax Amount',
            'State/UT Tax Amount',
            'Cess Amount'
        ]
        return columns

    def getInvoiceData(self, active_ids, invoiceType):
        mainData = []
        jsonData = []
        count = 0
        ctx = dict(self._context or {})
        b2csDataDict = {}
        b2csJsonDataDict = {}
        b2clJsonDataDict = {}
        b2bDataDict = {}
        hsnDict = {}
        hsnDataDict = {}
        reverseCharge = 'N'
        if ctx.get('gst_id'):
            resId = ctx.get('gst_id')
            resObj = self.env['gstr1.tool'].browse(resId)
            if resObj.reverse_charge:
                reverseCharge = 'Y'
        for active_id in active_ids:
            invData = {}
            invoiceObj = self.env['account.invoice'].browse(active_id)
            currency = invoiceObj.currency_id
            invoiceNumber = invoiceObj.number
            if len(invoiceNumber) > 16:
                invoiceNumber = invoiceNumber[0:16]
            invoiceDate = invoiceObj.date_invoice
            invoiceJsonDate = datetime.strptime(invoiceDate, '%Y-%m-%d').strftime('%d-%m-%Y')
            invoiceDate = datetime.strptime(invoiceDate, '%Y-%m-%d').strftime('%d-%b-%Y')
            invoiceTotal = invoiceObj.amount_total * currency.rate
            invoiceObj.inr_total = invoiceTotal
            invoiceTotal = round(invoiceTotal, 2)
            state = invoiceObj.partner_id.state_id
            code = state.x_tin or 0
            code = _unescape(state.x_tin)
            sname = _unescape(state.name)            
            stateName = "{}-{}".format(code, sname)
            data = []
            if invoiceType == 'b2b':
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    "pos": code,
                    "rchrg": reverseCharge,
                    "etin": "",
                    "inv_typ": "R"
                }
                data.extend([invoiceObj.x_vat, invoiceNumber, invoiceDate, invoiceTotal, stateName, reverseCharge, 'Regular', ''])
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, data)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                if b2bDataDict.get(invoiceObj.x_vat):
                    b2bDataDict[invoiceObj.x_vat].append(invData)
                else:
                    b2bDataDict[invoiceObj.x_vat] = [invData]
            elif invoiceType == 'b2cl':
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    "etin": "",
                }
                data.extend([invoiceNumber, invoiceDate, invoiceTotal, stateName])
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, data)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                if b2clJsonDataDict.get(code):
                    b2clJsonDataDict[code].append(invData)
                else:
                    b2clJsonDataDict[code] = [invData]
            elif invoiceType == 'b2cs':
                invData = {
                    "pos": code
                }
                b2bData = ['OE', stateName]
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, b2bData)
                b2bData = respData[0]
                rateDataDict = respData[2]
                rateJsonDict = respData[3]
                if b2csDataDict.get(stateName):
                    for key in rateDataDict.keys():
                        if b2csDataDict.get(stateName).get(key):
                            for key1 in rateDataDict.get(key).keys():
                                if b2csDataDict.get(stateName).get(key).get(key1):
                                    b2csDataDict.get(stateName).get(key)[key1] = b2csDataDict.get(stateName).get(key)[key1] + rateDataDict.get(key)[key1]
                                else:
                                    b2csDataDict.get(stateName).get(key)[key1] = rateDataDict.get(key)[key1]
                        else:
                            b2csDataDict.get(stateName)[key] = rateDataDict[key]
                else:
                    b2csDataDict[stateName] = rateDataDict
                if b2csJsonDataDict.get(code):
                    for key in rateJsonDict.keys():
                        if b2csJsonDataDict.get(code).get(key):
                            for key1 in rateJsonDict.get(key).keys():
                                if b2csJsonDataDict.get(code).get(key).get(key1):
                                    if key1 in ['rt', 'sply_ty', 'typ']:
                                        continue
                                    b2csJsonDataDict.get(code).get(key)[key1] = b2csJsonDataDict.get(code).get(key)[key1] + rateJsonDict.get(key)[key1]
                                    b2csJsonDataDict.get(code).get(key)[key1] = round(b2csJsonDataDict.get(code).get(key)[key1], 2)
                                else:
                                    b2csJsonDataDict.get(code).get(key)[key1] = rateJsonDict.get(key)[key1]
                        else:
                            b2csJsonDataDict.get(code)[key] = rateJsonDict[key]
                else:
                    b2csJsonDataDict[code] = rateJsonDict
                if respData[1]:
                    invData.update(respData[1][0])
            elif invoiceType == 'export':
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    "sbpcode": "",
                    "sbnum": "",
                    "sbdt": "",
                }
                data.extend([invoiceObj.export, invoiceNumber, invoiceDate, invoiceTotal, '', '', ''])
                respData = self.env['gst.invoice.data'].getGSTInvoiceData(invoiceObj, invoiceType, data)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                jsonData.append(invData)
            elif invoiceType == 'hsn':
                respData = self.env['gst.hsn.data'].getHSNData(invoiceObj, count, hsnDict, hsnDataDict)
                data = respData[0]
                jsonData.extend(respData[1])
                hsnDict = respData[2]
                hsnDataDict = respData[3]
                invoiceObj.gst_status = 'ready_to_upload'
            if data:
                mainData.extend(data)
        if b2csJsonDataDict:
            for pos,val in b2csJsonDataDict.items():
                for line in val.values():
                    line['pos'] = pos
                    jsonData.append(line)
        if b2csDataDict:
            b2csData = []
            for state, data in b2csDataDict.items():
                for rate, val in data.items():
                    b2csData.append(['OE', state, rate, round(val['taxval'], 2), round(val['cess'], 2), ''])
            mainData = b2csData

        if b2bDataDict:
            for ctin, inv in b2bDataDict.items():
                jsonData.append({
                    'ctin':ctin,
                    'inv':inv
                })
        if b2clJsonDataDict:
            for pos, inv in b2clJsonDataDict.items():
                jsonData.append({
                    'pos':pos,
                    'inv':inv
                })
        if hsnDict:
            vals = hsnDict.values()
            hsnMainData = []
            for val in vals:
                hsnMainData.extend(val.values())
            mainData = hsnMainData
        if hsnDataDict:
            vals = hsnDataDict.values()
            hsnMainData = []
            for val in vals:
                hsnMainData.extend(val.values())
            jsonData = hsnMainData
        return [mainData, jsonData]

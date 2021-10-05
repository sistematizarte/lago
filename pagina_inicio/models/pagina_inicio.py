# -*- coding: utf-8 -*- 
# Part of Odoo. See LICENSE file for full copyright and licensing details. 
from odoo import models, fields, api
import psycopg2

class PaginaInicio(models.Model): 
    _name = 'pagina.inicio'

    def _get_default_pagina(self):
    	# return "<p><br></p><table class='table table-bordered'><tbody><tr><td><h2 style='text-align: center; '><font style='color: rgb(107, 173, 222);'>Bienvenidos a la Nave</font></h2><p style='margin-bottom: 10px; color: rgb(51, 51, 51); font-family: &quot;Lucida Sans Unicode&quot;, &quot;Lucida Grande&quot;, sans-serif; font-size: 14px; text-align: justify; background-color: rgb(248, 248, 248);'><font style='font-size: 12px;'>Satisfacer la gran demanda de asistencia legal que actualmente se ve ampliamente desatendida en sectores de escasos recursos venezolanos, así como fomentar la investigación y formación referente a la problemática judicial y legislativa que atraviesa el país.</font></p><p style='margin-bottom: 10px; color: rgb(51, 51, 51); font-family: &quot;Lucida Sans Unicode&quot;, &quot;Lucida Grande&quot;, sans-serif; font-size: 14px; text-align: justify; background-color: rgb(248, 248, 248);'><font style='font-size: 12px;'>La Fundación Pro Bono Venezuela, ProVene tiene como objetivos organizar, promover y difundir la práctica del trabajo pro bono en los abogados venezolanos para así poder fortalecer el acceso a la justicia en Venezuela..</font></p><p style='margin-bottom: 10px; color: rgb(51, 51, 51); font-family: &quot;Lucida Sans Unicode&quot;, &quot;Lucida Grande&quot;, sans-serif; font-size: 14px; text-align: justify; background-color: rgb(248, 248, 248);'><strong style='font-weight: bold;'><font style='font-size: 12px;'>ORGANIZAMOS</font></strong><font style='font-size: 12px;'>&nbsp;el trabajo pro bono de las firmas de abogado, distribuyéndoles casos pro bono de forma periódica e involucrándolos con la formación e investigación jurídica sobre los temas de interés en las comunidades.</font></p><p style='margin-bottom: 10px; color: rgb(51, 51, 51); font-family: &quot;Lucida Sans Unicode&quot;, &quot;Lucida Grande&quot;, sans-serif; font-size: 14px; text-align: justify; background-color: rgb(248, 248, 248);'><strong style='font-weight: bold;'><font style='font-size: 12px;'>PROMOVEMOS</font></strong><font style='font-size: 12px;'>&nbsp;la incorporación de nuevos abogados a la práctica del trabajo pro bono.</font></p><p style='margin-bottom: 10px; color: rgb(51, 51, 51); font-family: &quot;Lucida Sans Unicode&quot;, &quot;Lucida Grande&quot;, sans-serif; font-size: 14px; text-align: justify; background-color: rgb(248, 248, 248);'><strong style='font-weight: bold;'><font style='font-size: 12px;'>DIFUNDIMOS</font></strong><font style='font-size: 12px;'>&nbsp;a través de todos los medios posibles los logros del trabajo pro bono en Venezuela para lograr incluir a nuevos miembros y voluntarios a nuestra fundación.</font></p><p style='margin-bottom: 10px; color: rgb(51, 51, 51); font-family: &quot;Lucida Sans Unicode&quot;, &quot;Lucida Grande&quot;, sans-serif; font-size: 14px; text-align: justify; background-color: rgb(248, 248, 248);'><strong style='font-weight: bold;'><font style='font-size: 12px;'>FORTALECEMOS</font></strong><font style='font-size: 12px;'>&nbsp;el acceso a la justicia en Venezuela, brindado la posibilidad a personas sin recursos de acceder a un abogado y tramitar sus necesidades legales.</font></p></td><td><p></p><div class='media_iframe_video' data-oe-expression='//www.youtube.com/embed/s7ib0FO28mU?autoplay=1&amp;mute=1&amp;rel=0&amp;loop=1&amp;playlist=s7ib0FO28mU&amp;controls=0'><div class='css_editable_mode_display'>&nbsp;</div><div class='media_iframe_video_size' contenteditable='false'>&nbsp;</div><iframe src='//www.youtube.com/embed/s7ib0FO28mU?autoplay=1&amp;mute=1&amp;rel=0&amp;loop=1&amp;playlist=s7ib0FO28mU&amp;controls=0' frameborder='0' contenteditable='false'></iframe></div><br><p></p></td></tr></tbody></table>"
        return '<div class="o_readonly"><table><tr><td><img alt="" src="/pagina_inicio/static/description/image.png" style="width: 100%;"/></td></tr></table></div>'

    cuadro_1 = fields.Char(string = 'Inicio', default= _get_default_pagina, readonly=True) 


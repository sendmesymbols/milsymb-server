from cStringIO import StringIO
from functools import wraps
from flask import abort
from flask import Response
import flask
from jmsml import Sidc, InvalidSidcLength, MilSymbol, InvalidSidc
from milsymbserver import app
from os.path import join
import xml.etree.ElementTree as ET

ET.register_namespace('', "http://www.w3.org/2000/svg")
NAMESPACE = "{http://www.w3.org/2000/svg}"


def ns_tag(tag_name, namespace=NAMESPACE):
    return "%s%s" % (namespace, tag_name)


def return_svg(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, mimetype='image/svg+xml')

    return decorated_function


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/sidc/<sic>/')
@return_svg
def sic(sic):
    try:
        symb = MilSymbol(sic)
    except InvalidSidc:
        app.logger.error('Invalid symbol identification code')
        abort(404)

    merged_svg = merge_svgs([symb.frame_fn, symb.main_icon_fn, symb.mod_one_fn, symb.mod_two_fn])
    f = StringIO()
    merged_svg.write(f, xml_declaration=True, encoding='utf-8')
    return f.getvalue()



def merge_svgs(list_of_file_names):
    main_svg = ET.parse(list_of_file_names[0])
    root = main_svg.getroot()
    root.insert(0, ET.Comment("Generated by XXX"))
    for g in root.findall(ns_tag('g')):
        if "id" in g.attrib:
            g.attrib.pop("id")
        if g.get('display', '') == "none":
            root.remove(g)
    for file_name in list_of_file_names[1:] :
        if not file_name:
            continue
        svg = ET.parse(file_name)
        for g in svg.getroot().findall(ns_tag('g')):
            if "id" in g.attrib:
                g.attrib.pop("id")
            if g.get('display', '') != "none":
                root.append(g)
    return main_svg


@app.route('/testsymbol')
@return_svg
def testsymbol():
    symb = MilSymbol('10031000161211002019')
    merged_svg = merge_svgs([symb.frame_fn, symb.main_icon_fn])
    f = StringIO()
    merged_svg.write(f, xml_declaration=True, encoding='utf-8')
    return f.getvalue()
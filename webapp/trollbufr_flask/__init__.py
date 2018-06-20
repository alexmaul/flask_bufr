from __future__ import print_function
import os.path
from trollbufr import bufr, load_file
from flask import Flask, request, url_for, render_template, redirect, Markup

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50000


BUFR_TABLES_TYPE = "libdwd"
BUFR_TABLES_DIR = os.path.join(os.path.dirname(__file__), "tables")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/decode', methods=['GET', 'POST'])
@app.route('/decode/<typ>', methods=['GET', 'POST'])
def decode(typ=None):
    if request.method == 'POST':
        fobj = request.files['the_file']
        data = fobj.stream.read()
        if typ is not None:
            how = typ
        else:
            how = request.form["decode"]
        if "JSON" in how or "json" in how:
            return json(data)
        else:
            return render_template("result.html", decoded=human(data))
    else:
        return redirect(url_for("index"))


def json(data):
    from flask import jsonify
    bufr_obj = bufr.Bufr(BUFR_TABLES_TYPE, BUFR_TABLES_DIR)
    decoded_list = []
    try:
        for blob_obj, _, header in load_file.next_bufr(bin_data=data):
            json_dict = {"heading": header,
                         "index": len(decoded_list)}
            try:
                json_obj = bufr_obj.decode(blob_obj, as_array=True)
                json_dict["bufr"] = json_obj
            except StandardError as e:
                json_dict["error"] = str(e)
            decoded_list.append(json_dict)
    except Warning or StandardError as broke:
        decoded_list.append({"index": len(decoded_list),
                             "error": broke.__str__()})
    return jsonify(decoded_list)


def human(data):
    decoded_list = []
    decoded_ahl = []
    idx = 1
    try:
        for blob_obj, _, header in load_file.next_bufr(bin_data=data):
            head = header or str(idx)
            idx += 1
            decoded_ahl.append(head)
            decoded_list.extend(("<h3><a name='", head, "'>BUFR #", head, "</a></h3>"))
            decoded_list.append("<pre>")
            decoded_list.append(pretty(blob_obj))
            decoded_list.append("</pre>")
    except Warning or StandardError as broke:
        decoded_list.extend(("<b>", broke.__str__(), "</b>"))
    cont_lst = ["<ul>"]
    for head in decoded_ahl:
        cont_lst.extend(("<li><a href='#", head, "'>BUFR #", head, "</a></li>"))
    cont_lst.append("</ul>")
    return Markup("{}<p>{}".format("".join(cont_lst), "".join(decoded_list)))


def pretty(blob_obj):
    import StringIO
    from trollbufr.coder.bufr_types import TabBType
    bufr_obj = bufr.Bufr(BUFR_TABLES_TYPE, BUFR_TABLES_DIR)
    fh_out = StringIO.StringIO()
    try:
        bufr_obj.decode_meta(blob_obj, load_tables=False)
        tabl = bufr_obj.load_tables()
        print("META:\n%s"
              % bufr_obj.get_meta_str(),
              end="<br/>", file=fh_out)
        for report in bufr_obj.next_subset():
            print("SUBSET\t#%d/%d"
                  % (report.subs_num[0] + 1, report.subs_num[1]),
                  end="<br/>", file=fh_out)
            for descr_entry in report.next_data():
                if descr_entry.mark is not None:
                    if isinstance(descr_entry.value, (list)):
                        descr_value = "".join([str(x) for x
                                               in descr_entry.value
                                               if x is not None])
                    else:
                        descr_value = descr_entry.value or ""
                    print("  ",
                          descr_entry.mark,
                          descr_value,
                          end="", file=fh_out)
                    print(end="<br/>", file=fh_out)
                    continue
                d_name, d_unit, d_typ = tabl.lookup_elem(descr_entry.descr)
                if d_typ in (TabBType.CODE, TabBType.FLAG):
                    if descr_entry.value is None:
                        print("%06d %-40s = Missing value"
                              % (descr_entry.descr, d_name),
                              end="<br/>", file=fh_out)
                    else:
                        v = tabl.lookup_codeflag(descr_entry.descr,
                                                 descr_entry.value)
                        print("%06d %-40s = %s"
                              % (descr_entry.descr,
                                 d_name,
                                 str(v)),
                              end="<br/>", file=fh_out)
                else:
                    if d_unit in ("CCITT IA5", "Numeric"):
                        d_unit = ""
                    if descr_entry.value is None:
                        print("%06d %-40s = /// %s"
                              % (descr_entry.descr,
                                 d_name, d_unit),
                              end="<br/>", file=fh_out)
                    elif descr_entry.quality is not None:
                        print("%06d %-40s = %s %s (%s)"
                              % (descr_entry.descr,
                                 d_name,
                                 str(descr_entry.value),
                                 d_unit,
                                 descr_entry.quality),
                              end="<br/>", file=fh_out)
                    else:
                        print("%06d %-40s = %s %s"
                              % (descr_entry.descr,
                                 d_name,
                                 str(descr_entry.value),
                                 d_unit),
                              end="<br/>", file=fh_out)
    except StandardError as e:
        print("ERROR\t%s" % e, end="<br/>", file=fh_out)
    out_text = fh_out.getvalue()
    fh_out.close()
    return out_text


def run():
    app.run()


if __name__ == "__main__":
    app.run()

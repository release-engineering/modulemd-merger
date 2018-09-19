import traceback

import flask
import werkzeug.exceptions as exc
import gi
gi.require_version('Modulemd', '1.0')
from gi.repository import Modulemd  # noqa

app = flask.Flask('modulemd-merger')


@app.errorhandler(500)
def error(e):
    """ Return tracebacks to users so they can understand what went wrong. """
    return traceback.format_exc(), 500


@app.route('/merge', methods=["POST"])
def merge():
    """ The only endpoint.

    Submit a JSON POST request with a list of modulemd documents.

    Returns in plaintext the merged modulemd.
    """

    data = flask.request.get_json()

    validate(data)

    prioritizer = Modulemd.Prioritizer()
    for entry in data['documents']:
        objects = Modulemd.objects_from_string(entry['modulemd'])
        priority = entry.get('priority', 0)
        prioritizer.add(objects, priority)

    merged_objects = prioritizer.resolve()
    return Modulemd.dumps(merged_objects)


@app.route('/healthcheck', methods=["GET"])
def healthcheck():
    return "OK"


def validate(data):
    """ Validation, to give some human readable error messages back. """
    if not data:
        raise exc.BadRequest("Only JSON POST data is permitted.")

    if 'documents' not in data:
        raise exc.BadRequest("'documents' is a required json field.")

    if not isinstance(data['documents'], list):
        raise exc.BadRequest("'documents' must be a list.")

    for document in data['documents']:
        if not isinstance(document, dict):
            raise exc.BadRequest("Every document must be a dict.  "
                                 "%r is not." % document)

        if 'modulemd' not in document:
            raise exc.BadRequest("Every document must include a 'modulemd' "
                                 "field.  %r does not." % document)

        if not isinstance(document.get('priority', 0), int):
            raise exc.BadRequest("The 'priority' value must be an int.")

from .indices import IndexManager
from whoosh.qparser import MultifieldParser
from whoosh.collectors import TimeLimitCollector, TimeLimit


class Searcher(object):
    def __init__(self):
        self.index = IndexManager().get()

    def search(self, string, limit=25, facet=None, proxy=True):
        fields = [u"name", u"comment", u"product", u"categories"]
        qp = MultifieldParser(
            fields,
            self.index.schema,
            fieldboosts={u"name": 5., u"categories": 2., u"product": 3.}
        )
        with self.index.searcher() as searcher:
            if facet is None:
                results = [
                    dict(obj.iteritems())
                    for obj in searcher.search(qp.parse(string), limit=limit)
                ]
            else:
                results = {
                    k: [searcher.stored_fields(i) for i in v] for k, v in
                    searcher.search(qp.parse(string), groupedby=facet
                                    ).groups().iteritems()}
        if proxy and facet is not None:
            # TODO: Use get_activity
            return results
        elif proxy:
            return results
        else:
            return results

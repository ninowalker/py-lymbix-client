from django.db import models
from django.db.models import Model, FloatField, IntegerField, CharField, Manager
from django.conf import settings
from lymbix import Client

__ALL__ = ['LymbixScore']

LYMBIX_METRICS = ['affection_friendliness',
                  'amusement_excitement',
                  'anger_loathing',
                  'average_intensity',
                  'clarity',
                  'contentment_gratitude',
                  'coverage',
                  'enjoyment_elation',
                  'fear_uneasiness',
                  'humiliation_shame',
                  'sadness_grief']

class LymbixScoreManager(Manager):
    CLIENT = None
    
    def score_item(self, content, item_int_pk, save=True):
        data = self._client().tonalize(content, item_int_pk)
        obj = self._create_item(data, item_int_pk)
        if save:
            obj.save()
        return obj        
        
    def _create_item(self, data, item_pk):
        obj = LymbixScore(reference_id = item_pk,
                          sentiment = data.get('article_sentiment',{}).get('score',0))
        for metric in LYMBIX_METRICS:
            setattr(obj, metric, data.get(metric))
        return obj
    
    def _client(self):
        if not self.CLIENT:
            if hasattr(settings, 'LYMBIX_API_KEY'):
                self.CLIENT = Client(settings.LYMBIX_API_KEY)
            elif hasattr(settings, 'LYMBIX_CLIENT_FACTORY_FUNCTION'):
                fun = settings.LYMBIX_CLIENT_FACTORY_FUNCTION
                if callable(fun):
                    self.CLIENT = fun()
                elif type(fun) == str and "." in fun:
                    last_ind = fun.rfind(".")
                    mod = __import__(fun[0:last_ind])
                    func = getattr(mod, fun[last_ind+1:])
                    self.CLIENT = func()
                else:
                    raise AttributeError("settings value for LYMBIX_CLIENT_FACTORY_FUNCTION "
                                         " does not reference callable function or string reference to a module and function; e.g. a.b.function")
                assert isinstance(self.CLIENT, Client), "Client initialization function did not create an instance of lymbix.Client: %s" % type(self.CLIENT)
        return self.CLIENT
                        

class LymbixScore(models.Model):
    affection_friendliness = FloatField()
    amusement_excitement = FloatField()
    anger_loathing = FloatField()
    average_intensity = FloatField()
    clarity = FloatField()
    contentment_gratitude = FloatField()
    coverage = FloatField()
    enjoyment_elation = FloatField()
    fear_uneasiness = FloatField()
    humiliation_shame = FloatField()
    sadness_grief = FloatField()

    dominant_emotion = CharField(max_length=24)
    sentiment = FloatField()
    reference_id = IntegerField(db_index=True)

    objects = LymbixScoreManager()

"""
{u'affection_friendliness': 0.05,
 u'amusement_excitement': 0.46,
 u'anger_loathing': -0.4,
 u'article': u'Fast and crazy.',
 u'article_sentiment': {u'score': -0.21, u'sentiment': u'Negative'},
 u'average_intensity': 1.21,
 u'clarity': 44.23,
 u'contentment_gratitude': 0.02,
 u'coverage': 13.0,
 u'dominant_emotion': u'fear_uneasiness',
 u'enjoyment_elation': 0.19,
 u'fear_uneasiness': -1.71,
 u'humiliation_shame': -1.06,
 u'ignored_terms': [u'Fast'],
 u'intense_sentence': {u'dominant_emotion': u'fear_uneasiness',
                       u'intensity': 1.7,
                       u'sentence': u'Fast and crazy.'},
 u'sadness_grief': -0.95}
 """
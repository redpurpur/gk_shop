from django import template

register = template.Library()


def cut_words(value, length=3):
    return value[:length]+'...'


register.filter('cut_words', cut_words)


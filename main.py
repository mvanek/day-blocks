#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.ext import ndb
import jinja2
import os
import datetime
import logging

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Record(ndb.Model):
    start_date = ndb.DateProperty()
    dates = ndb.IntegerProperty(repeated=True)
    name = ndb.StringProperty(required=True)

    @property
    def calendar(self):
        prev_set = -1
        for next_set in self.dates:
            for i in range(prev_set + 1, next_set):
                yield (False, self.start_date + datetime.timedelta(i))
            yield (True, self.start_date + datetime.timedelta(next_set))
            prev_set = next_set
        today = (datetime.datetime.now().date() - self.start_date).days
        for i in range(prev_set + 1, today + 1):
            yield (False, self.start_date + datetime.timedelta(i))

    def set_start(self, date):
        diff = (date - self.start_date).days
        self.start_date = date
        self.dates = sorted(map(lambda d: d - diff, self.dates))

    def set_name(self, name):
        self.name = name

    def set_date(self, date):
        if self.start_date is None or self.dates is None:
            self.start_date = date
            self.dates = [0]
            return
        diff = date - self.start_date
        diff_days = diff.days
        if diff_days < 0:
            '''Date is earlier than first date'''
            self.start_date = date
            self.dates = sorted([0] + map(lambda d: d - diff_days, self.dates))
        elif diff_days not in self.dates:
            self.dates.append(diff_days)
            self.dates = sorted(self.dates)

    def unset_date(self, date):
        diff_days = (date - self.start_date).days
        if diff_days == 0:
            '''Need to change start date'''
            del self.dates[0]
            try:
                diff_dates = self.dates[0]
                self.dates = map(lambda d: d - diff_dates, self.dates)
            except IndexError:
                self.start_date = None
                self.dates = None
                return
            self.start_date += datetime.timedelta(diff_dates)
        elif diff_days > 0:
            '''Just delete'''
            try:
                self.dates.remove(diff_days)
            except ValueError:
                pass

class RecordHandler(webapp2.RequestHandler):
    def get(self):
        record = Record.get_by_id(int(self.request.path.split('/')[2]))
        if not record:
            self.abort(404)
        template = JINJA_ENVIRONMENT.get_template('record.jinja2')
        self.response.write(template.render(record=record))

    def post(self):
        record = Record.get_by_id(int(self.request.path.split('/')[2]))
        if not record:
            self.abort(404)
        method = self.request.get('method')
        if method == 'set_name':
            record.set_name(self.request.get('name'))
        else:
            date = datetime.date(*map(int, self.request.get('date').split('-')))
            if method == 'set':
                record.set_date(date)
            elif method == 'unset':
                record.unset_date(date)
            elif method == 'set_start':
                record.set_start(date)
        record.put()
        if method == 'set_start' or method == 'set_name':
            self.redirect(self.request.path)

class RecordListHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.jinja2')
        records = Record.query()
        self.response.write(template.render(records=records))

    def post(self):
        start_date = datetime.date(*map(int, self.request.get('start_date').split('-')))
        name = self.request.get('name')
        record = Record(name=name, start_date=start_date)
        logging.info(record.put())
        self.redirect('/r/')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/r/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/r/', RecordListHandler),
    ('/r/.*', RecordHandler)
], debug=True)

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
from collections import namedtuple
from urllib import unquote
from google.appengine.ext import ndb
import os
import jinja2
import datetime
import logging

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_ENVIRONMENT.globals['datetime'] = datetime

Streak = namedtuple('Streak', ['length', 'start_date'])
Day = namedtuple('Day', ['set', 'date'])


class Record(ndb.Model):
    start_date = ndb.DateProperty()
    user = ndb.StringProperty()
    dates = ndb.IntegerProperty(repeated=True)
    name = ndb.StringProperty(required=True)

    @property
    def calendar(self):
        prev_set = -1
        for next_set in self.dates:
            if next_set < 0:
                continue
            for i in range(prev_set + 1, next_set):
                yield Day(False, self.start_date + datetime.timedelta(i))
            yield Day(True, self.start_date + datetime.timedelta(next_set))
            prev_set = next_set
        today = (datetime.datetime.now().date() - self.start_date).days
        for i in range(prev_set + 1, today + 1):
            yield Day(False, self.start_date + datetime.timedelta(i))

    @property
    def latest_streak(self):
        current = None
        for s in self.streaks:
            current = s
        return current

    @property
    def longest_streak(self):
        try:
            return max(self.streaks, key=lambda s: s.length)
        except ValueError:
            return None

    @property
    def streaks(self):
        dates = iter(self.dates)
        prev = next(dates)
        streak_start = self.start_date + datetime.timedelta(prev)
        streak_len = 0
        for d in dates:
            streak_len += 1
            if d - prev - 1:
                # streak is over
                yield Streak(streak_len, streak_start)
                streak_len = 0
                streak_start = self.start_date + datetime.timedelta(d)
            prev = d
        else:
            yield Streak(streak_len + 1, streak_start)

    def set_start(self, date):
        diff = (date - self.start_date).days
        self.start_date = date
        self.dates = sorted(map(lambda d: d - diff, self.dates))

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
            record.name = self.request.get('name')
        elif method == 'set_user':
            record.user = self.request.get('user')
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
        self.response.write(template.render(
            records=records,
            start_date=datetime.datetime.now().date()-datetime.timedelta(104)
        ))

    def post(self):
        start_date = datetime.date(*map(int, self.request.get('start_date').split('-')))
        name = self.request.get('name')
        user = self.request.get('user')
        if not user:
            user = None
        record = Record(name=name, start_date=start_date, user=user)
        logging.info(record.put())
        self.redirect('/r/')

class UserHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.jinja2')
        user = unquote(self.request.path.split('/')[2])
        records = Record.query(Record.user == user)
        self.response.write(template.render(records=records, user=user))

class UserListHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('users.jinja2')
        qry = Record.query(projection=['user'], distinct=True).order(Record.user)
        users = [r.user for r in qry]
        self.response.write(template.render(users=users))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/r/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/u/', UserListHandler),
    ('/u/.*', UserHandler),
    ('/r/', RecordListHandler),
    ('/r/.*', RecordHandler)
], debug=True)

#! /usr/bin/python
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004 Dr. Ralf Schlatterbeck Open Source Consulting.
# Reichergasse 131, A-3411 Weidling.
# Web: http://www.runtux.com Email: office@runtux.com
# All rights reserved
# ****************************************************************************
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# ****************************************************************************

def uni (latin1) :
    return latin1.decode ('latin1').encode ('utf8')

prettymap = \
{ 'abo'              : uni('Abo')
, 'abos'             : uni('Abos')
, 'abo_price'        : uni('Preis')
, 'aboprice'         : uni('Abo Preis')
, 'abo_type'         : uni('Abo-Typ')
, 'abotype'          : uni('Abotyp')
, 'activity'         : uni('letzte �nderung')
, 'address'          : uni('Adresse')
, 'adr_type'         : uni('Typ')
, 'amount'           : uni('Betrag')
, 'author'           : uni('Autor')
, 'balance_open'     : uni('Offen')
, 'begin'            : uni('Beginn')
, 'bookentry'        : uni('Buchung am')
, 'changed'          : uni('ge�ndert')
, 'city'             : uni('Ort')
, 'code'             : uni('Code')
, 'confirm'          : uni('Best�tigung Passwort')
, 'content'          : uni('Inhalt')
, 'country'          : uni('Land')
, 'countrycode'      : uni('L�ndercode')
, 'currency'         : uni('W�hrung')
, 'date'             : uni('Datum')
, 'date_payed'       : uni('Bezahlt am')
, 'description'      : uni('Beschreibung')
, 'email'            : uni('Email')
, 'end'              : uni('Storniert per')
, 'fax'              : uni('Fax')
, 'files'            : uni('Dateien')
, 'firstname'        : uni('Vorname')
, 'function'         : uni('Funktion')
, 'history'          : uni('Liste der �nderungen')
, 'id'               : uni('ID')
, 'invoice'          : uni('Rechnung')
, 'invoices'         : uni('Rechnungen')
, 'invoice_no'       : uni('RgNr')
, 'invoice_template' : uni('Rechnungsvorlage')
, 'invoice_level'    : uni('Mahnstufe')
, 'lastname'         : uni('Nachname')
, 'last_sent'        : uni('verschickt am')
, 'letter'           : uni('Brief')
, 'lettertitle'      : uni('Brief-Titel')
, 'messages'         : uni('Notizen')
, 'msg'              : uni('Notiz')
, 'n_sent'           : uni('Mahnstufe')
, 'name'             : uni('Name')
, 'o_invoices'       : uni('offene Rechnungen')
, 'open'             : uni('offen')
, 'order'            : uni('Sortiernummer')
, 'password'         : uni('Passwort')
, 'payed_abos'       : uni('Zahler f�r')
, 'payer'            : uni('Zahler')
, 'payment'          : uni('Zahlung')
, 'period'           : uni('Laufzeit')
, 'period_start'     : uni('Datum von')
, 'period_end'       : uni('Datum bis')
, 'phone'            : uni('Telefon')
, 'phone_home'       : uni('Telefon privat')
, 'phone_mobile'     : uni('Telefon mobil')
, 'phone_office'     : uni('Telefon Gesch�ft')
, 'realname'         : uni('Name')
, 'receipt_no'       : uni('BelegNr')
, 'recipients'       : uni('Empf�nger')
, 'postalcode'       : uni('PLZ')
, 'remove'           : uni('l�schen')
, 'salutation'       : uni('Anrede')
, 'street'           : uni('Strasse')
, 'subject'          : uni('Betreff')
, 'subscriber'       : uni('Abonnent')
, 'tmplate'          : uni('Vorlage')
, 'title'            : uni('Titel')
, 'username'         : uni('Login Name')
, 'valid'            : uni('g�ltig')
}

def pretty (name) :
    return (prettymap.get (name, name))

def abo_max_invoice (db, abo) :
    if not len (abo ['invoices']) :
        return None
    maxinv  = db.invoice.getnode (abo ['invoices'][0])
    maxdate = maxinv ['period_end']
    for i in abo ['invoices'] :
        inv = db.invoice.getnode (i)
        d   = inv ['period_end']
        if maxdate < d :
            maxdate = d
            maxinv  = inv
    return maxinv
# end def abo_max_invoice

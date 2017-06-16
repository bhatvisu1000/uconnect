import { Injectable } from '@angular/core';


import { Storage } from '@ionic/storage';

import { Http, Response } from "@angular/http";
import { Headers, RequestOptions } from '@angular/http';
import 'rxjs/Rx';
import {Observable} from 'rxjs/Observable';

import {SendRequest} from "../models/SendRequest"

@Injectable()
export class HttpService {
private registrationUrl = 'http://localhost:5000/requestPost';

constructor(private http: Http) {}

	submitRequest(sendRequest: SendRequest): Observable<Response>  {
	  
	  let headers = new Headers({ 'Content-Type': 'application/json' });
	  return this.http
	    .post(this.registrationUrl, JSON.stringify(sendRequest), {headers: headers});
	 }
}
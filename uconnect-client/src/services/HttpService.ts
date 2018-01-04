import { Injectable } from '@angular/core';




import { Http, Response } from "@angular/http";
import { Headers } from '@angular/http';
import 'rxjs/Rx';
import {Observable} from 'rxjs/Observable';

import {SendRequest} from "../models/SendRequest"

@Injectable()
export class HttpService {
private registrationUrl = 'http://localhost:5008/requestPost';

constructor(private http: Http) {}

	submitRequest(sendRequest: SendRequest): Observable<Response>  {
	  console.log(JSON.stringify(sendRequest));
	  let headers = new Headers({ 'Content-Type': 'application/json' });
	  return this.http
	    .post(this.registrationUrl, JSON.stringify(sendRequest), {headers: headers});
	 }
}	
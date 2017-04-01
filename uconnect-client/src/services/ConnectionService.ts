import { Injectable } from "@angular/core";
import { Http, Response } from "@angular/http";
import 'rxjs/Rx';
import { Headers, RequestOptions } from '@angular/http';

import {ConnectionSummary} from "../models/connection/ConnectionSummary"

@Injectable()
export class ConnectionService {
  private connectionSummarys: ConnectionSummary[] = [];

  constructor(private http: Http) {
  }


  fetchList(token: string) {
    console.log('ConnectionService');
    let headers = new Headers({ 'Content-Type': 'application/json' });
    /**console.log(JSON.stringify(this.http.get('http://localhost:3000/ConnectionSummary/').map((response: Response) => response.json())));
    **/
    //return this.http.get('http://localhost:3000/ConnectionSummary/')
    return this.http.get('http://localhost:5000/getAllMembers/1', headers)
        	.map((response: Response) => {
        return response.json();
      })
      .do((connectionSummarys: ConnectionSummary[]) => {
        if (connectionSummarys) {
          this.connectionSummarys = connectionSummarys
        } else {
          this.connectionSummarys = [];
        }
      });

  }

private getHeaders(){
    let headers = new Headers();
    headers.append('Accept', 'application/json');
    return headers;
  }
 }
import { Injectable } from "@angular/core";
import { Http, Response } from "@angular/http";
import 'rxjs/Rx';

import {Connections} from "../models/connection/Connections"

import {SendRequest} from "../models/SendRequest"
import {Request} from "../models/Request"
import {Header} from "../models/Header"
import {MyResponse} from "../models/MyResponse"
import {ResponseReceived} from "../models/ResponseReceived"
import {Auth} from "../models/connection/Auth"
import {LoginRequestData} from "../models/login/LoginRequestData"


@Injectable()
export class ConnectionService {
  private connectionSummarys: Connections[] = [];

  private request: Request = null;
  private loginRequestData: LoginRequestData = null;
  private auth: Auth = null;
  public responseReceived: ResponseReceived = null
  private header:  Header = null;
  public sendRequest: SendRequest = null;

  constructor(private http: Http) {
  }


  createRequest(authKey: string, loginid: string, entityId: string): SendRequest  {
    this.auth = new Auth(loginid, "Web/Mobile", "", "IOS", "Mobile", "SDFSDKLGHASKLDFGHSAKLFG214ADFA",  "Member", "1.1", "aaabbbccc", authKey, entityId);
    
    this.loginRequestData = new LoginRequestData(this.auth);
    
    
    this.header= new Header("Member", "getAMemberDetail", "None");

    
    this.request= new Request(this.header, this.loginRequestData);

    this.sendRequest= new SendRequest(this.request);


    console.log(this.request);
    console.log("registeration Service json data " +     JSON.stringify(this.sendRequest));
    console.log(JSON.stringify(this.sendRequest));
    
    return this.sendRequest;
  }

private getHeaders(){
    let headers = new Headers();
    headers.append('Accept', 'application/json');
    return headers;
  }
 }
import { Injectable } from "@angular/core";
import { Http } from "@angular/http";
import 'rxjs/Rx';

import {Connections} from "../models/connection/Connections"

import {SendRequest} from "../models/SendRequest"
import {Request} from "../models/Request"
import {Header} from "../models/Header"
//import {MyResponse} from "../models/MyResponse"
import {ResponseReceived} from "../models/ResponseReceived"
import {Auth} from "../models/connection/Auth"
import {SearchConnection} from "../models/member/SearchConnection"

import {AuthService} from "./AuthService"
import {LoginRequestData} from "../models/login/LoginRequestData"
import {UpdateConnectionRequest} from "../models/connection/UpdateConnectionRequest"
import {SQLStorageService} from "./SQLStorageService"

@Injectable()
export class ConnectionService {
  private connections: Connections = null;

  private request: Request = null;
  private loginRequestData: LoginRequestData = null;
  private auth: Auth = null;
  public responseReceived: ResponseReceived = null;
  private header:  Header = null;
  public sendRequest: SendRequest = null;
  private updateConnectionRequest: UpdateConnectionRequest = null;
  private searchConnection: SearchConnection = null;
  
  

  constructor(private http: Http, private sqlStorageService: SQLStorageService) {
    
  }


  createRequest(auth: Auth): SendRequest  {
    this.auth = auth;
    
    this.loginRequestData = new LoginRequestData(this.auth);
    
    
    this.header= new Header("Member", "getAMemberDetail", "None");

    
    this.request= new Request(this.header, this.loginRequestData);

    this.sendRequest= new SendRequest(this.request);


    console.log(this.request);
    console.log("registeration Service json data " +     JSON.stringify(this.sendRequest));
    console.log(JSON.stringify(this.sendRequest));
    
    return this.sendRequest;
  }

/*private getHeaders(){
    let headers = new Headers();
    headers.append('Accept', 'application/json');
    return headers;
  }
  */
  createDeleteRequest(memberId: string) {
    
    this.header= new Header("Member", "getAMemberDetail", "None");

    
    this.request= new Request(this.header, this.loginRequestData);

    this.sendRequest= new SendRequest(this.request);


    console.log(this.request);
    console.log("registeration Service json data " +     JSON.stringify(this.sendRequest));
    console.log(JSON.stringify(this.sendRequest));
    
    return this.sendRequest;
  }

createSearchRequest(auth: Auth, searchInputRequestData: string, page: String, loaclAuthService: AuthService) {
    
    
    this.searchConnection = new SearchConnection(searchInputRequestData, page, auth);
    
    this.header= new Header("Member", "SearchMember", "None");

    
    this.request= new Request(this.header, this.searchConnection);

    this.sendRequest= new SendRequest(this.request);
    
    
    console.log(this.request);
    console.log("registeration Service json data " +     JSON.stringify(this.sendRequest));
    console.log(JSON.stringify(this.sendRequest));
    
    return this.sendRequest;
  }


  createUpdateConnectionsRequest(memberId: string, action: string) {

    this.header= new Header("Member", "UpdateConnectionDetails", "None");

    let connectionArray: Array<Connections> = new Array();
    if(action == 'Favorite') {
      this.connections = new Connections(null, null, null, '1', memberId, null, null, "Member", action);
    }else if(action == 'UnFavorite') {
      this.connections = new Connections(null, null, null, '0', memberId, null, null, "Member", 'Favorite');
    }else if(action == 'Remove') {
      this.connections = new Connections(null, null, null, '0', memberId, null, null, "Member", action);
    }else{
      this.connections = new Connections(null, null, null, '0', memberId, null, null, "Member", action);
    }
    connectionArray.push(this.connections);
    this.updateConnectionRequest = new UpdateConnectionRequest(connectionArray, this.auth);
    this.request= new Request(this.header, this.updateConnectionRequest);

    this.sendRequest= new SendRequest(this.request);


    console.log(this.request);
    console.log("registeration Service json data " +     JSON.stringify(this.sendRequest));
    console.log(JSON.stringify(this.sendRequest));
    
    return this.sendRequest;
  }

}
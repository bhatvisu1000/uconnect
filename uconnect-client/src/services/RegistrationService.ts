import { Injectable } from "@angular/core";
import { Http, Response } from "@angular/http";
import {Observable} from 'rxjs/Observable';
import { Headers, RequestOptions } from '@angular/http';
import 'rxjs/Rx';

import {SendRequest} from "../models/SendRequest"
import {Request} from "../models/Request"
import {Header} from "../models/Header"
import {MainArg} from "../models/MainArg"
import {MyResponse} from "../models/Response"
import {Address} from "../models/connection/Address"
import {Main} from "../models/connection/Main"
import {Contact} from "../models/connection/Contact"
import {Auth} from "../models/connection/Auth"
import {RegistrationRequestData} from "../models/registration/RegistrationRequestData"
import {HttpService} from "./HttpService"

import {ResponseReceived} from "../models/ResponseReceived"

import {RegistrationPage} from "../pages/registration/registration"


@Injectable()
export class RegistrationService {
  private request: Request = null;
  private mainArg: MainArg = null;
  private registrationRequestData: RegistrationRequestData = null;
  private auth: Auth = null;
  private main: Main = null;
  private address: Address = null;
  private contact: Contact = null;
  
  private header:  Header = null;
  private sendRequest: SendRequest = null;
  
  private registrationUrl = 'http://localhost:5000/requestPost';
  constructor(private httpService: HttpService) {
  }

 createMember(userName: string, password: string, firstName: string,
            lastName: string,
            zipCode: string) {
    this.main = new Main(firstName, lastName, "sanju", "M", "Member");
    
    this.address = new Address("", "", "", zipCode, "", "");
    this.contact = new Contact(userName, "");
    
    this.auth = new Auth(userName, "Web/Mobile", password, "IOS", "Mobile", "SDFSDKLGHASKLDFGHSAKLFG214ADFA",  "Member", "1.1", "aaabbbccc", "", "");
    
    this.registrationRequestData = new RegistrationRequestData(this.auth, this.main, this.address, this.contact);
    
    
    this.header= new Header("Registration", "RegisterEntity", "None");

    
    this.request= new Request(this.header, this.registrationRequestData);

    this.sendRequest= new SendRequest(this.request);
    
    
    console.log("main" + this.main);
    console.log("address" + this.address);
    console.log("contact" + this.contact);

    console.log(this.request);
    console.log("registeration Serive json data " +     JSON.stringify(this.sendRequest) + " url " + this.registrationUrl);
    console.log(JSON.stringify(this.sendRequest));
  }

  
 submitMember(registrationPage: RegistrationPage) {
  this.httpService.submitRequest(this.sendRequest)
    .subscribe(
        (response: Response) => {
          const responseReceived: ResponseReceived = response.json();
          console.log(responseReceived); 
          
         },
        err => console.log('error ' + err.json().message),
        () => console.log('Authentication Complete')
      );
 }
 

 /*submitMember(): Observable<MyResponse> {
  
  let headers = new Headers({ 'Content-Type': 'application/json' });
  let options = new RequestOptions({ headers: headers });
  return this.http
    .post(this.registrationUrl, JSON.stringify(this.sendRequest), options)
    .map(this.extractData)
    .catch(this.handleError);
 }*/

private extractData(res: Response) {
        let body = res.json();
        console.log('while extractData RegisterationService' + body);
        return body.data || {};
    }
private handleError(error: Response) {
        console.error(error);
        return Observable.throw(error.json().error || 'Server Error');
    }

/**addProduct(product: Product) {                
        let body = JSON.stringify(product);            
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let options = new RequestOptions({ headers: headers });

        return this.http.post(this.productsUrl, body, options)
            .map(this.extractData)
            .catch(this.handleError);
    }

    private extractData(res: Response) {
        let body = res.json();
        return body.data || {};
    }

    private handleError(error: Response) {
        console.error(error);
        return Observable.throw(error.json().error || 'Server Error');
    }
*/
 }
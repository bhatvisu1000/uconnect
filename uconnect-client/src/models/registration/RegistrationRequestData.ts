import { MainArg } from "../MainArg";
import { Main } from "../connection/Main";
import { Address } from "../connection/Address";
import { Contact } from "../connection/Contact";
import { Auth } from "../connection/Auth";

export class RegistrationRequestData extends MainArg {
  constructor(public Auth: Auth, public Main: Main, public Address: Address, public Contact: Contact) {

  super();
  }
}		
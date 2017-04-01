import { Main } from "./connection/Main";
import { Address } from "./connection/Address";
import { Contact } from "./connection/Contact";

export class MainArg {
  constructor(public Main: Main, public Address: Address, public Contact: Contact) {}
}
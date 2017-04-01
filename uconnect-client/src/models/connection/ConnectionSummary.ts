import { Address } from "./Address";
import { Contact } from "./Contact";
import { Main } from "./Main";

export class ConnectionSummary {
  constructor(public address: Address, public contact: Contact, public main: Main) {}
}
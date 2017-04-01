import { Header } from "./Header";
import { MainArg } from "./MainArg";

export class Request {
  constructor(public Header: Header, public MainArg: MainArg) {}
}
import { Header } from "./Header";
import { MainArg } from "./MainArg";

export class Response {
  constructor(public Header: Header, public MainArg: MainArg) {}
}
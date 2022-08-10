#include "parse-head"

Parser::Parser(void)
{
	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
		errmsg("Create socket file descriptor fail.");
	if (!(host = gethostbyname(API_MAIN.c_str())))
		errmsg("Get API fail.");
	full_addr(addr);
	if (connect(sockfd, (struct sockaddr *)&addr, sizeof(struct sockaddr)) < 0)
		errmsg("Connect API fail.");
	string msg = make_header("GET", "/get", API_MAIN.c_str());
	if (write(sockfd, msg.c_str(), msg.size()) < 0)
		errmsg("Send request fail.");
	buffer = new char [2000];
	while ((recvbyte = read(sockfd, buffer + recvbytes, SOCKETSIZE - recvbytes)) > 0)
		recvbytes += recvbyte;
}

string Parser::make_header(const char *method, const char *path, const char *host) const
{
	string header = method;
	header = header + " " + path + " HTTP/1.1\r\n" +
		"Host: " + host + "\r\nAccept: " + ACCEPT +
		"\r\nUser-Agent: " + USER_AGENT + "\r\n" +
		"Connection: " + CONNECTION + "\r\n" +
		"\r\n";
	return header;
}

void Parser::full_addr(struct sockaddr_in &addr)
{
	addr.sin_family = AF_INET;
	if (host)
		addr.sin_addr = *((in_addr *)host->h_addr_list[0]);
	else
		errmsg("Find addr error.");
	addr.sin_port = PORT;
}

void Parser::errmsg(const string &__msg) const
{
	cerr << ERRMSG << __msg << endl;
	exit(EXIT_FAILURE);
}

void Parser::warnmsg(const string &__msg) const
{
	cerr << WARNMSG << __msg << endl;
}

void Parser::show(void) const
{
	cout << buffer << endl;
}

Parser::~Parser(void)
{
	cout << "The Object is end." << endl;
	delete [] buffer;
}
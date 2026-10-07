/* Bounded real TCP exchange through the emulated NIC; host verifies every byte. */
static void networkCheck(const char *label,DWORD phase) {
    WSADATA data;SOCKET s;static struct sockaddr_in address;u_long nonblocking=1;
    fd_set writes,errors;struct timeval timeout;int error,errorSize,n,offset;
    DWORD round,i,ms=5000;static BYTE tx[4096],rx[4096];
    if(WSAStartup(MAKEWORD(2,0),&data))fatal("FAIL_WSA_START");
    s=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);if(s==INVALID_SOCKET)fatal("FAIL_SOCKET");
    address.sin_family=AF_INET;
    address.sin_port=htons(4597);address.sin_addr.s_addr=inet_addr("10.0.2.2");
    if(ioctlsocket(s,FIONBIO,&nonblocking))fatal("FAIL_NONBLOCK");
    n=connect(s,(struct sockaddr*)&address,sizeof(address));
    if(n==SOCKET_ERROR&&WSAGetLastError()!=WSAEWOULDBLOCK)fatal("FAIL_CONNECT");
    FD_ZERO(&writes);FD_ZERO(&errors);FD_SET(s,&writes);FD_SET(s,&errors);timeout.tv_sec=5;timeout.tv_usec=0;
    if(select(0,NULL,&writes,&errors,&timeout)!=1||!FD_ISSET(s,&writes)||FD_ISSET(s,&errors))fatal("FAIL_CONNECT_WAIT");
    error=0;errorSize=sizeof(error);
    if(getsockopt(s,SOL_SOCKET,SO_ERROR,(char*)&error,&errorSize)||error)fatal("FAIL_CONNECT_STATUS");
    nonblocking=0;
    if(ioctlsocket(s,FIONBIO,&nonblocking)||setsockopt(s,SOL_SOCKET,SO_RCVTIMEO,(char*)&ms,sizeof(ms))||setsockopt(s,SOL_SOCKET,SO_SNDTIMEO,(char*)&ms,sizeof(ms)))fatal("FAIL_SOCKET_TIMEOUT");
    for(round=0;round<32;round++) {
        for(i=0;i<sizeof(tx);i++)tx[i]=(BYTE)(phase*97+round*13+i*7);
        offset=0;while(offset<(int)sizeof(tx)){n=send(s,(char*)tx+offset,sizeof(tx)-offset,0);if(n<=0)fatal("FAIL_SEND");offset+=n;}
        offset=0;while(offset<(int)sizeof(rx)){n=recv(s,(char*)rx+offset,sizeof(rx)-offset,0);if(n<=0)fatal("FAIL_RECV");offset+=n;}
        for(i=0;i<sizeof(rx);i++)if(rx[i]!=(BYTE)(tx[i]^0xa5))fatal("FAIL_NETWORK_BYTES");
    }
    if(shutdown(s,SD_SEND))fatal("FAIL_SOCKET_SHUTDOWN");
    if(recv(s,(char*)rx,1,0)!=0)fatal("FAIL_NETWORK_EOF");
    if(closesocket(s)||WSACleanup())fatal("FAIL_SOCKET_CLOSE");
    record(label,32,131072,131072);
}


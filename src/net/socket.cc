/* -*-mode:c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */

#include <sys/socket.h>
#include <netinet/in.h>
#include <linux/netfilter_ipv4.h>

#include "socket.hh"
#include "exception.hh"

using namespace std;

/* default constructor for socket of (subclassed) domain and type */
Socket::Socket( const int domain, const int type )
    : FileDescriptor( SystemCall( "socket", socket( domain, type, 0 ) ) )
{}

/* construct from file descriptor */
Socket::Socket( FileDescriptor && fd, const int domain, const int type )
    : FileDescriptor( move( fd ) )
{
    int actual_value;
    socklen_t len;

    /* verify domain */
    len = getsockopt( SOL_SOCKET, SO_DOMAIN, actual_value );
    if ( (len != sizeof( actual_value )) or (actual_value != domain) ) {
        throw runtime_error( "socket domain mismatch" );
    }

    /* verify type */
    len = getsockopt( SOL_SOCKET, SO_TYPE, actual_value );
    if ( (len != sizeof( actual_value )) or (actual_value != type) ) {
        throw runtime_error( "socket type mismatch" );
    }
}

/* get the local or peer address the socket is connected to */
Address Socket::get_address( const std::string & name_of_function,
                             const std::function<int(int, sockaddr *, socklen_t *)> & function ) const
{
    Address::raw address;
    socklen_t size = sizeof( address );

    SystemCall( name_of_function, function( fd_num(),
                                            &address.as_sockaddr,
                                            &size ) );

    return Address( address, size );
}

Address Socket::local_address() const
{
    return get_address( "getsockname", getsockname );
}

Address Socket::peer_address() const
{
    return get_address( "getpeername", getpeername );
}

/* bind socket to a specified local address (usually to listen/accept) */
void Socket::bind( const Address & address )
{
    SystemCall( "bind", ::bind( fd_num(),
                                &address.to_sockaddr(),
                                address.size() ) );
}

/* connect socket to a specified peer address */
void Socket::connect( const Address & address )
{
    SystemCall( "connect", ::connect( fd_num(),
                                      &address.to_sockaddr(),
                                      address.size() ) );
}

/* send datagram to specified address */
void UDPSocket::sendto( const Address & destination, const string & payload )
{
    const ssize_t bytes_sent =
        SystemCall( "sendto", ::sendto( fd_num(),
                                        payload.data(),
                                        payload.size(),
                                        0,
                                        &destination.to_sockaddr(),
                                        destination.size() ) );

    register_write();

    if ( size_t( bytes_sent ) != payload.size() ) {
        throw runtime_error( "datagram payload too big for sendto()" );
    }
}

/* send datagram to connected address */
void UDPSocket::send( const string & payload )
{
    const ssize_t bytes_sent =
        SystemCall( "send", ::send( fd_num(),
                                    payload.data(),
                                    payload.size(),
                                    0 ) );

    register_write();

    if ( size_t( bytes_sent ) != payload.size() ) {
        throw runtime_error( "datagram payload too big for send()" );
    }
}

/* mark the socket as listening for incoming connections */
void TCPSocket::listen( const int backlog )
{
    SystemCall( "listen", ::listen( fd_num(), backlog ) );
}

/* accept a new incoming connection */
TCPSocket TCPSocket::accept()
{
    register_read();
    return TCPSocket( FileDescriptor( SystemCall( "accept", ::accept( fd_num(), nullptr, nullptr ) ) ) );
}

/* get socket option */
template <typename option_type>
socklen_t Socket::getsockopt( const int level, const int option, option_type & option_value ) const
{
    socklen_t optlen = sizeof( option_value );
    SystemCall( "getsockopt", ::getsockopt( fd_num(), level, option,
                                            &option_value, &optlen ) );
    return optlen;
}

/* set socket option */
template <typename option_type>
void Socket::setsockopt( const int level, const int option, const option_type & option_value )
{
    SystemCall( "setsockopt", ::setsockopt( fd_num(), level, option,
                                            &option_value, sizeof( option_value ) ) );
}

/* allow local address to be reused sooner, at the cost of some robustness */
void Socket::set_reuseaddr()
{
    setsockopt( SOL_SOCKET, SO_REUSEADDR, int( true ) );
}

void UDPSocket::set_timestamps()
{
    setsockopt( SOL_SOCKET, SO_TIMESTAMPNS, int( true ) );
}

pair<Address, string> UDPSocket::recvfrom()
{
    static const ssize_t RECEIVE_MTU = 65536;

    /* receive source address and payload */
    Address::raw datagram_source_address;
    char buffer[ RECEIVE_MTU ];

    socklen_t fromlen = sizeof( datagram_source_address );

    ssize_t recv_len = SystemCall( "recvfrom",
                                   ::recvfrom( fd_num(),
                                               buffer,
                                               sizeof( buffer ),
                                               MSG_TRUNC,
                                               &datagram_source_address.as_sockaddr,
                                               &fromlen ) );

    if ( recv_len > RECEIVE_MTU ) {
        throw runtime_error( "recvfrom (oversized datagram)" );
    }

    register_read();

    return make_pair( Address( datagram_source_address, fromlen ),
                      string( buffer, recv_len ) );
}

Address TCPSocket::original_dest() const
{
    Address::raw dstaddr;
    socklen_t len = getsockopt( SOL_IP, SO_ORIGINAL_DST, dstaddr );

    return Address( dstaddr, len );
}

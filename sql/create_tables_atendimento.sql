create table clientes (
    id_cliente int generated always as identity primary key,
    nome text not null,
    email text not null unique,
    telefone text not null
);

create table atendentes (
    id_atendente int generated always as identity primary key,
    nome text not null,
    email text not null unique,
    telefone text not null,
    senha text not null
);

create table chamados (
    id_chamado int generated always as identity primary key,
    id_cliente int not null,
    id_atendente int default null,
    nome text not null,
    descricao text not null,
    data_abertura timestamp default current_timestamp,
    data_fechamento timestamp default null,
    status text not null default 'aberto'
        check (status in ('aberto', 'em andamento', 'resolvido')),
    foreign key (id_cliente) references clientes(id_cliente),
    foreign key (id_atendente) references atendentes(id_atendente)
);
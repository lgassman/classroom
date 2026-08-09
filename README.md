# Classroom

GitHub course administration tool for managing courses and assignments in a teaching organization.

Classroom is a command-line application designed to simplify the administration of programming courses using GitHub. It helps instructors manage courses, student rosters, assignments, repositories, and feedback repositories without having to perform these operations manually through the GitHub web interface.

## Table of Contents

### English

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [GitHub Client Configuration](#github-client-configuration)
- [Courses](#courses)
- [Assignments](#assignments)
- [License](#license)

### Español

- [Propósito](#propósito)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración del cliente de GitHub](#configuración-del-cliente-de-github)
- [Cursos](#cursos)
- [Assignments](#assignments-1)
- [Licencia](#licencia)

---

# English

## Purpose

Classroom is intended for instructors who use GitHub as part of their courses.

The application provides a command-line interface for managing a GitHub organization used for a course. It can:

- configure and authenticate a GitHub client;
- create and manage courses;
- keep track of courses locally;
- create assignments from GitHub template repositories;
- create one repository per student;
- create repositories for specific GitHub users, such as teachers;
- inspect assignments and their repositories.

The application is designed to automate repetitive administrative tasks while keeping the GitHub organization as the source of truth for repositories and users.

## Prerequisites

Before using Classroom, you need:

- **Python 3.14 or newer**.
- A **GitHub organization** that will contain the course repositories.
- A GitHub account with sufficient administrative permissions in that organization.
- A GitHub OAuth App configured for the application.

The GitHub user used by Classroom must have the permissions required to create repositories, manage teams and memberships, and perform the other administrative operations required by the application.

## Installation

Clone this repository and install the application using your preferred Python environment.

For example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

After installation, the `classroom` command should be available:

```bash
classroom --help
```

Each command also provides its own help:

```bash
classroom client --help
classroom login --help
classroom logout --help
classroom whoami --help
classroom course --help
classroom assignment --help
```

Some commands provide additional examples and explanations through their epilog:

```bash
classroom course --help
classroom assignment --help
```

## GitHub Client Configuration

Classroom uses a GitHub OAuth App to authenticate users.

### Create a GitHub OAuth App

In GitHub, go to:

https://github.com/settings/developers

and open **OAuth Apps**.

Create a new OAuth App and configure the application according to the authentication flow used by Classroom.

GitHub provides a **Client ID** and **Client Secret** for the application.

The Client ID and Client Secret can then be configured with:

```bash
classroom client CLIENT_ID CLIENT_SECRET
```

For example:

```bash
classroom client my-client-id my-client-secret
```

The configured client ID can be inspected with:

```bash
classroom client
```

The client secret can be explicitly requested with:

```bash
classroom client --show-secret
```

Both values can be removed with:

```bash
classroom client --delete
```

### Local storage

Classroom deliberately stores the two pieces of information differently.

The **Client Secret** is sensitive and is stored using the operating system's keyring through the `keyring` Python package. The secret is therefore not stored as plain text in the application's configuration files.

The **Client ID**, which is not considered a secret, is stored as part of Classroom's local configuration.

Classroom uses `platformdirs` to determine the appropriate operating-system-specific directory for this configuration. `platformdirs` does not itself store the configuration; it provides the application with a standard location in which to do so.

The same configuration directory can also be used for other persistent application settings required by future Classroom features.

After configuring the client, authenticate with GitHub using:

```bash
classroom login
```

The authenticated user can be checked with:

```bash
classroom whoami
```

## Courses

A course represents a course section managed by Classroom.

A course is identified by:

- GitHub organization;
- academic year;
- semester;
- course section.

For example:

```bash
classroom course -o obj1unq -y 2026 -s 2 -c 2 roster.txt
```

The roster file contains one GitHub username per line.

### Current course

Classroom can keep a **current course** so that it does not have to be specified in every command.

For example:

```bash
classroom course -o obj1unq -y 2026 -s 2 -c 2 --set-current
```

After that, commands that operate on a course can omit the organization, year, semester, and course options:

```bash
classroom assignment -t https://github.com/obj1unq/pepitaEnunciado
```

The current course is only a convenience for commands that operate on a course. Commands that modify the definition of a course require the course to be specified explicitly, helping prevent accidental modifications to the wrong course.

The current course can be cleared with:

```bash
classroom course --unset
```

### Tracked courses

Classroom also keeps track of courses locally.

Tracked courses act as a **memory aid**: they allow the application to remember courses that have been configured previously, even when they are not the current course.

To see the current course and tracked courses:

```bash
classroom course
```

A course can be removed from the local tracked-course configuration with:

```bash
classroom course -o obj1unq -y 2026 -s 2 -c 2 --untrack
```

Untracking a course only removes the local reference. It does not delete the course or its GitHub resources.

### Updating a course

An existing course can be updated by providing a new roster:

```bash
classroom course -o obj1unq -y 2026 -s 2 -c 2 --update roster.txt
```

### Deleting a course

A course can be deleted with:

```bash
classroom course -o obj1unq -y 2026 -s 2 -c 2 --delete
```

Course modification commands require the course to be explicitly specified.

## Assignments

An assignment is created from a GitHub template repository.

For example:

```bash
classroom assignment -t https://github.com/obj1unq/pepitaEnunciado
```

If no name is specified, the template repository name is used as the assignment name.

A custom name can be provided with:

```bash
classroom assignment \
    -t https://github.com/obj1unq/pepitaEnunciado \
    -n tp1
```

The `--private` option creates private student repositories:

```bash
classroom assignment \
    -t https://github.com/obj1unq/pepitaEnunciado \
    --private
```

### What happens when an assignment is created?

For each student in the course team, Classroom creates a repository in the course organization.

Repository names follow this convention:

```text
COURSE_ASSIGNMENT_USERNAME
```

For example:

```text
obj1unq-2026s2c2_pepitaEnunciado_lgassman
obj1unq-2026s2c2_pepitaEnunciado_dfortini
```

The student is then added as a collaborator with the appropriate permissions.

Classroom also creates the `feedback` branch and the feedback baseline used by the feedback workflow.

The repository is then prepared so that a pull request can be used to compare the student's work against the feedback baseline.

### Creating repositories for specific users

Normally, an assignment is created for every student in the course.

The `--user` option allows specific GitHub users to be processed instead:

```bash
classroom assignment \
    -t https://github.com/obj1unq/pepitaEnunciado \
    --user lgassman otro_usuario
```

This is useful when an instructor also needs an assignment repository for themselves, for example to prepare or test feedback.

The users specified with `--user` replace the course roster for that operation; they are not added to the list of students.

### Listing assignments

To list all assignments for the current course:

```bash
classroom assignment
```

A specific course can be selected explicitly:

```bash
classroom assignment -o obj1unq -y 2026 -s 2 -c 2
```

Classroom searches the organization's repositories using the course prefix and determines the assignment names from the repository naming convention.

The output also shows how many repositories have been generated for each assignment.

### Inspecting an assignment

To inspect the repositories belonging to a particular assignment:

```bash
classroom assignment -n tp1
```

Classroom lists the repositories belonging to the assignment and indicates:

- whether the repository corresponds to a student in the course;
- the number of commits in the repository's default branch.

At the end, it reports students who:

- do not have a repository for the assignment;
- have a repository but have not made any commits beyond the feedback baseline.

## License

Classroom is free software distributed under the terms of the **GNU General Public License v3.0 (GPLv3)**.

You are free to use, copy, modify, and redistribute the software. If you redistribute modified versions, the resulting work must remain available under the GPLv3 and its corresponding source code must be made available under the terms of the license.

See the [`LICENSE`](LICENSE) file for the complete license text.

---

# Español

## Propósito

Classroom es una herramienta de línea de comandos pensada para docentes que utilizan GitHub en sus cursos.

La aplicación proporciona una interfaz para administrar una organización de GitHub utilizada en una materia. Permite:

- configurar y autenticar un cliente de GitHub;
- crear y administrar cursos;
- mantener un registro local de cursos;
- crear assignments a partir de repositorios template de GitHub;
- crear un repositorio por estudiante;
- crear repositorios para usuarios específicos de GitHub, como docentes;
- consultar assignments y sus repositorios.

El objetivo es automatizar tareas administrativas repetitivas, manteniendo a la organización de GitHub como fuente de verdad para los repositorios y usuarios.

## Requisitos previos

Para utilizar Classroom se necesita:

- **Python 3.14 o superior**.
- Una **organización de GitHub** que contenga los repositorios de los cursos.
- Un usuario de GitHub con permisos administrativos suficientes dentro de esa organización.
- Una GitHub OAuth App configurada para la aplicación.

El usuario utilizado por Classroom debe tener los permisos necesarios para crear repositorios, administrar equipos y membresías y realizar las demás operaciones administrativas requeridas.

## Instalación

Cloná este repositorio e instalá la aplicación utilizando el entorno de Python que prefieras.

Por ejemplo:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Después de instalarla, el comando `classroom` debería estar disponible:

```bash
classroom --help
```

Cada comando tiene además su propia ayuda:

```bash
classroom client --help
classroom login --help
classroom logout --help
classroom whoami --help
classroom course --help
classroom assignment --help
```

Algunos comandos incluyen ejemplos y explicaciones adicionales:

```bash
classroom course --help
classroom assignment --help
```

## Configuración del cliente de GitHub

Classroom utiliza una GitHub OAuth App para autenticar a los usuarios.

### Crear una GitHub OAuth App

En GitHub, ingresá a:

https://github.com/settings/developers

y abrí la sección **OAuth Apps**.

Creá una nueva OAuth App y configurala de acuerdo con el flujo de autenticación utilizado por Classroom.

GitHub proporcionará un **Client ID** y un **Client Secret** para la aplicación.

Estos valores se pueden configurar en Classroom mediante:

```bash
classroom client CLIENT_ID CLIENT_SECRET
```

Por ejemplo:

```bash
classroom client my-client-id my-client-secret
```

Para consultar el Client ID configurado:

```bash
classroom client
```

Para mostrar explícitamente el Client Secret:

```bash
classroom client --show-secret
```

Para eliminar ambos valores:

```bash
classroom client --delete
```

### Almacenamiento local

Classroom almacena ambos valores de manera diferente.

El **Client Secret** es información sensible y se almacena mediante el keyring del sistema operativo utilizando el paquete Python `keyring`. De esta manera, el secret no se guarda como texto plano en los archivos de configuración de la aplicación.

El **Client ID**, que no es un secreto, se almacena como parte de la configuración local de Classroom.

Classroom utiliza `platformdirs` para determinar el directorio apropiado para esa configuración según el sistema operativo. `platformdirs` no almacena la configuración por sí mismo: proporciona a la aplicación una ubicación estándar donde hacerlo.

Ese mismo directorio de configuración puede utilizarse para otras configuraciones persistentes que necesiten futuras funcionalidades de Classroom.

Una vez configurado el cliente, iniciá sesión con:

```bash
classroom login
```

Para consultar el usuario autenticado:

```bash
classroom whoami
```

## Cursos

Un curso representa una comisión administrada por Classroom.

Un curso se identifica mediante:

- organización de GitHub;
- año académico;
- semestre;
- número de comisión.

Por ejemplo:

```bash
classroom course -o obj1unq -y 2026 -s 2 -c 2 roster.txt
```

El archivo de roster contiene un usuario de GitHub por línea.

### Curso actual

Classroom permite establecer un **curso actual**, de modo que no sea necesario especificarlo en cada comando.

Por ejemplo:

```bash
classroom course -o obj1unq -y 2026 -s 2 -c 2 --set-current
```

A partir de ese momento, los comandos que operan sobre un curso pueden omitir la organización, año, semestre y comisión:

```bash
classroom assignment -t https://github.com/obj1unq/pepitaEnunciado
```

El curso actual es solamente una comodidad para los comandos que operan sobre un curso. Los comandos que modifican la definición de un curso requieren que el curso sea especificado explícitamente, para reducir el riesgo de modificar accidentalmente el curso equivocado.

El curso actual se puede limpiar con:

```bash
classroom course --unset
```

### Cursos trackeados

Classroom también mantiene localmente una lista de cursos trackeados.

Los cursos trackeados funcionan como una **ayuda memoria**: permiten recordar cursos que fueron configurados anteriormente aunque no sean el curso actual.

Para consultar el curso actual y la lista de cursos trackeados:

```bash
classroom course
```

Un curso puede eliminarse de la configuración local mediante:

```bash
classroom course -o obj1unq -y 2026 -s 2 -c 2 --untrack
```

Destrackear un curso solamente elimina la referencia local. No elimina el curso ni sus recursos de GitHub.

### Actualizar un curso

Un curso existente puede actualizarse proporcionando un nuevo roster:

```bash
classroom course -o obj1unq -y 2026 -s 2 -c 2 --update roster.txt
```

### Eliminar un curso

Un curso puede eliminarse mediante:

```bash
classroom course -o obj1unq -y 2026 -s 2 -c 2 --delete
```

Los comandos que modifican cursos requieren que el curso sea especificado explícitamente.

## Assignments

Un assignment se crea a partir de un repositorio template de GitHub.

Por ejemplo:

```bash
classroom assignment -t https://github.com/obj1unq/pepitaEnunciado
```

Si no se especifica un nombre, se utiliza como nombre del assignment el nombre del repositorio template.

También se puede indicar un nombre personalizado:

```bash
classroom assignment \
    -t https://github.com/obj1unq/pepitaEnunciado \
    -n tp1
```

La opción `--private` permite crear repositorios privados:

```bash
classroom assignment \
    -t https://github.com/obj1unq/pepitaEnunciado \
    --private
```

### ¿Qué sucede al crear un assignment?

Para cada estudiante del equipo del curso, Classroom crea un repositorio dentro de la organización.

Los nombres siguen la convención:

```text
CURSO_ASSIGNMENT_USUARIO
```

Por ejemplo:

```text
obj1unq-2026s2c2_pepitaEnunciado_lgassman
obj1unq-2026s2c2_pepitaEnunciado_dfortini
```

Luego se agrega al estudiante como colaborador con los permisos correspondientes.

Classroom también crea la rama `feedback` y el baseline utilizado por el mecanismo de feedback.

Finalmente, el repositorio queda preparado para utilizar un pull request que permita comparar el trabajo del estudiante con el baseline de feedback.

### Crear repositorios para usuarios específicos

Normalmente, un assignment se crea para todos los estudiantes del curso.

La opción `--user` permite procesar usuarios específicos de GitHub:

```bash
classroom assignment \
    -t https://github.com/obj1unq/pepitaEnunciado \
    --user lgassman otro_usuario
```

Esto resulta útil cuando un docente necesita tener también un repositorio del assignment, por ejemplo para preparar o probar el feedback.

Los usuarios especificados mediante `--user` reemplazan al roster del curso para esa operación; no se agregan a la lista de estudiantes.

### Listar los assignments

Para listar todos los assignments del curso actual:

```bash
classroom assignment
```

También se puede especificar explícitamente el curso:

```bash
classroom assignment -o obj1unq -y 2026 -s 2 -c 2
```

Classroom busca los repositorios de la organización utilizando el prefijo del curso y obtiene los nombres de los assignments a partir de la convención de nombres de los repositorios.

El resultado también indica cuántos repositorios fueron generados para cada assignment.

### Consultar un assignment

Para consultar los repositorios correspondientes a un assignment particular:

```bash
classroom assignment -n tp1
```

Classroom lista los repositorios del assignment e indica:

- si el repositorio corresponde a un estudiante del curso;
- la cantidad de commits en la rama default del repositorio.

Al final informa los estudiantes que:

- no tienen un repositorio para ese assignment;
- tienen un repositorio pero no realizaron commits más allá del baseline de feedback.

## Licencia

Classroom es software libre distribuido bajo los términos de la **GNU General Public License v3.0 (GPLv3)**.

El software puede utilizarse, copiarse, modificarse y redistribuirse libremente. Si se redistribuye una versión modificada, el trabajo resultante debe mantenerse disponible bajo GPLv3 y su código fuente correspondiente debe estar disponible bajo los términos de la licencia.

Ver el archivo [`LICENSE`](LICENSE) para consultar el texto completo de la licencia.
